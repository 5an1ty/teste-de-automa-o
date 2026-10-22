import csv
import json
import tempfile
import unittest
from pathlib import Path
from dataclasses import replace
from src.models import Order, FIELDS, Result
from src.txt_reader import read_orders, read_operators
from src.order_validator import validar_ordem
from src.print_manager import imprimir_ordem
from src.sap_interface import SystemFailure, RealSap
from src.workflow import run
from src.config import load

VALID = Order('1894', 'Fechado', '0', '15', 'Manutenção', 'Pessoa fictícia', '00247', 'Operador fictício', '', '')
OPS = {'00247': 'Operador fictício'}

class FakeSap:
    def __init__(self, order=VALID, dialog=True, send_error=False, confirmed=True):
        self.order, self.dialog, self.send_error, self.confirmed = order, dialog, send_error, confirmed
        self.clicks = 0
        self.searches = []
    def buscar_ordem(self, numero):
        self.searches.append(numero)
        return self.order is not None
    def ler_dados_ordem(self): return self.order
    def confirmar_contexto(self, numero): return self.order.numero == numero
    def abrir_impressao(self, numero): return self.dialog
    def enviar_impressao(self):
        self.clicks += 1
        if self.send_error: raise RuntimeError('Falha após clique')
    def confirmar_envio(self): return True
    def confirmar_impressao_fisica(self): return self.confirmed

class ValidationTests(unittest.TestCase):
    def test_valid_and_leading_zeros(self):
        self.assertTrue(all(validar_ordem('1894', VALID, OPS).values()))
        self.assertFalse(validar_ordem('1894', replace(VALID, operador_id='247'), OPS)['OPERADOR_NAO_AUTORIZADO'])
    def test_invalid_fields(self):
        cases = [
            ('status','Aberto','STATUS_INVALIDO'), ('horas','-1','SEM_HORAS_CONSUMIDAS'),
            ('minutos','0','SEM_HORAS_CONSUMIDAS'), ('minutos','60','SEM_HORAS_CONSUMIDAS'),
            ('minutos','x','SEM_HORAS_CONSUMIDAS'), ('horas','','SEM_HORAS_CONSUMIDAS'),
            ('solicitante',' ','SOLICITANTE_VAZIO'), ('operador_id','999','OPERADOR_NAO_AUTORIZADO'),
            ('operador_nome','','OPERADOR_VAZIO'), ('tecnico_id','1','TECNICO_PREENCHIDO'),
            ('tecnico_nome','Pessoa','TECNICO_PREENCHIDO'), ('numero','1895','NUMERO_DIVERGENTE'),
            ('tipo','Metrologia','TIPO_ORDEM_INVALIDO')]
        for field, value, code in cases:
            with self.subTest(field=field,value=value):
                self.assertFalse(validar_ordem('1894', replace(VALID, **{field:value}), OPS)[code])
    def test_missing_read_and_not_found(self):
        for field in FIELDS:
            self.assertFalse(validar_ordem('1894', replace(VALID, legiveis=frozenset(FIELDS)-{field}), OPS)['CAMPO_ILEGIVEL'])
        self.assertEqual(validar_ordem('1894', None, OPS), {'ORDEM_NAO_ENCONTRADA':False})
    def test_collects_all_reasons(self):
        checks = validar_ordem('1894', replace(VALID,status='Aberto',solicitante='',tecnico_id='1'), OPS)
        self.assertEqual(sum(not v for v in checks.values()),3)
    def test_configurable_type(self):
        self.assertTrue(all(validar_ordem('1894', replace(VALID,tipo='Outro'), OPS,'Outro').values()))

class ReaderTests(unittest.TestCase):
    def test_files(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'input.txt'
            for content in ('', '1894\n1894', '1894\nx'):
                p.write_text(content)
                with self.assertRaises(ValueError): read_orders(p)
            p.write_text('\ufeff 001894 \n1895\n',encoding='utf-8')
            self.assertEqual(read_orders(p),['001894','1895'])
            for content in ('','247;A\n247;B','247','247;','x;A','247;A;B'):
                p.write_text(content)
                with self.assertRaises(ValueError): read_operators(p)
            p.write_text(' 00247 ; Exemplo \n',encoding='utf-8')
            self.assertEqual(read_operators(p),{'00247':'Exemplo'})

class PrintTests(unittest.TestCase):
    def approved(self):
        return Result('1894',resultado='APROVADA',verificacoes=validar_ordem('1894',VALID,OPS))
    def test_dry_run_never_clicks(self):
        sap=FakeSap(); result=self.approved()
        imprimir_ordem(sap,result)
        self.assertEqual(sap.clicks,0)
        self.assertFalse(result.enviada)
    def test_dialog_failure(self):
        sap=FakeSap(dialog=False); result=self.approved()
        with self.assertRaises(SystemFailure): imprimir_ordem(sap,result,enabled=True)
        self.assertEqual(sap.clicks,0)
        self.assertIn('FALHA_IMPRESSAO',result.motivos)
    def test_failure_after_click_no_retry(self):
        sap=FakeSap(send_error=True); result=self.approved()
        with self.assertRaises(SystemFailure): imprimir_ordem(sap,result,enabled=True)
        with self.assertRaises(SystemFailure): imprimir_ordem(sap,result,enabled=True)
        self.assertEqual(sap.clicks,1)
        self.assertEqual(result.impressao,'NAO_CONFIRMADA')
    def test_confirmation_states(self):
        for confirmed in (True, False):
            sap=FakeSap(confirmed=confirmed); result=self.approved()
            if confirmed: imprimir_ordem(sap,result,enabled=True)
            else:
                with self.assertRaises(SystemFailure): imprimir_ordem(sap,result,enabled=True)
            self.assertTrue(result.enviada)
            self.assertEqual(result.confirmada,confirmed)
    def test_rejected_and_context_blocked(self):
        with self.assertRaises(SystemFailure): imprimir_ordem(FakeSap(),Result('1894'),enabled=True)
        with self.assertRaises(SystemFailure): imprimir_ordem(FakeSap(replace(VALID,numero='1895')),self.approved(),enabled=True)

class WorkflowTests(unittest.TestCase):
    def test_reports_and_rejections_continue(self):
        with tempfile.TemporaryDirectory() as d:
            sap=FakeSap()
            results,path,stopped=run(['1894','1895'],OPS,sap,d)
            self.assertFalse(stopped)
            self.assertEqual([r.resultado for r in results],['APROVADA','REPROVADA'])
            self.assertEqual(sap.clicks,0)
            summary=json.loads((path/'resumo.json').read_text())
            self.assertEqual(summary['total'],2)
            self.assertEqual(summary['enviadas'],0)
            self.assertEqual(len((path/'tecnico.jsonl').read_text().splitlines()),2)
            with (path/'relatorio.csv').open(encoding='utf-8-sig') as stream:
                self.assertEqual(len(list(csv.DictReader(stream))),2)
    def test_not_found(self):
        with tempfile.TemporaryDirectory() as d:
            results,_,stopped=run(['1894'],OPS,FakeSap(None),d)
            self.assertFalse(stopped)
            self.assertEqual(results[0].motivos,['ORDEM_NAO_ENCONTRADA'])
    def test_manual_interrupt(self):
        with tempfile.TemporaryDirectory() as d:
            sap=FakeSap()
            results,_,stopped=run(['1894','1895'],OPS,sap,d,cancelled=lambda:True)
            self.assertTrue(stopped)
            self.assertEqual(sap.searches,[])
            self.assertIn('INTERRUPCAO_MANUAL',results[0].motivos)
            self.assertEqual(results[1].resultado,'NAO_PROCESSADA')
    def test_system_failure_stops_batch(self):
        with tempfile.TemporaryDirectory() as d:
            sap=FakeSap(replace(VALID,legiveis=frozenset()))
            results,_,stopped=run(['1894','1895'],OPS,sap,d)
            self.assertTrue(stopped)
            self.assertEqual(sap.searches,['1894'])
            self.assertTrue(results[0].falha_tecnica)
    def test_consultation_does_not_print(self):
        with tempfile.TemporaryDirectory() as d:
            results,_,_=run(['1894'],OPS,FakeSap(),d,mode='CONSULTA')
            self.assertEqual(results[0].impressao,'NAO_SOLICITADA')
    def test_duplicate_batch_blocked(self):
        with self.assertRaises(ValueError): run(['1894','1894'],OPS,FakeSap(),'unused')
    def test_real_adapter_blocked(self):
        with self.assertRaises(SystemFailure): RealSap()
    def test_real_config_blocked(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'config.json'
            path.write_text('{"mode":"CONSULTA"}')
            with self.assertRaises(ValueError): load(path)

if __name__ == '__main__': unittest.main()
