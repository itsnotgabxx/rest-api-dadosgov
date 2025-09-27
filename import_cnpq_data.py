#!/usr/bin/env python3
"""
Script para importação de dados do CNPq a partir de arquivo CSV
"""
import pandas as pd
import os
import sys
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# Adicionar o diretório raiz ao Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.models.beneficiario import Beneficiario
from app.models.instituicao import Instituicao
from app.models.programa import Programa
from app.models.pagamento import Pagamento
from app.core.database import Base

# Configuração do banco
DATABASE_URL = "sqlite:///./sql_app.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def parse_date(date_str):
    """
    Converte string de data para datetime.date
    """
    if pd.isna(date_str) or not date_str or date_str.strip() == '':
        return None
    
    try:
        # Formato: "01/09/2023 00:00"
        date_part = date_str.split(' ')[0]  # Remove a parte do horário
        return datetime.strptime(date_part, '%d/%m/%Y').date()
    except:
        try:
            # Tentar outros formatos
            return datetime.strptime(date_str, '%Y-%m-%d').date()
        except:
            return None

def parse_value(value_str):
    """
    Converte string de valor monetário para float
    """
    if pd.isna(value_str) or not value_str:
        return 0.0
    
    try:
        # Remove pontos de milhares e substitui vírgula por ponto
        value_clean = str(value_str).replace('.', '').replace(',', '.')
        return float(value_clean)
    except:
        return 0.0

def import_from_csv(csv_file_path: str):
    """
    Importa dados do CNPq a partir de arquivo CSV
    """
    if not os.path.exists(csv_file_path):
        print(f"Arquivo não encontrado: {csv_file_path}")
        return
        
    print(f"Lendo arquivo CSV: {csv_file_path}")
    
    try:
        # Ler CSV com separador de tabulação
        df = pd.read_csv(csv_file_path, sep=';', encoding='utf-8')
        print(f"Total de registros no CSV: {len(df)}")
        
        # Mostrar colunas disponíveis
        print("Colunas encontradas:")
        for i, col in enumerate(df.columns):
            print(f"   {i+1}. {col}")
            
        # Criar tabelas se não existirem
        Base.metadata.create_all(bind=engine)
        
        db = SessionLocal()
        
        try:
            # Limpar dados existentes (opcional)
            print("Limpando dados existentes...")
            db.query(Pagamento).delete()
            db.query(Beneficiario).delete()
            db.query(Instituicao).delete()
            db.query(Programa).delete()
            db.commit()
            
            # Caches para evitar duplicatas
            beneficiarios_cache = {}
            instituicoes_cache = {}
            programas_cache = {}
            
            stats = {
                'total_linhas': len(df),
                'processadas': 0,
                'beneficiarios': 0,
                'instituicoes': 0,
                'programas': 0,
                'pagamentos': 0,
                'erros': 0
            }
            
            # Processar dados
            for index, row in df.iterrows():
                if index % 1000 == 0:
                    print(f"Processando linha {index}...")
                    
                try:
                    # =================== BENEFICIÁRIO ===================
                    nome_beneficiario = str(row.get('BENEFICIARIO', '')).strip()
                    cpf_anonimizado = str(row.get('CPF ANONIMIZADO', '')).strip()
                    categoria_nivel = str(row.get('CATEGORIA_NIVEL', '')).strip()
                    
                    # Criar/buscar beneficiário
                    if cpf_anonimizado and cpf_anonimizado not in beneficiarios_cache:
                        beneficiario = Beneficiario(
                            nome=nome_beneficiario,
                            cpf_anonimizado=cpf_anonimizado,
                            categoria_nivel=categoria_nivel
                        )
                        db.add(beneficiario)
                        db.flush()  # Para obter o ID
                        beneficiarios_cache[cpf_anonimizado] = beneficiario.id
                        stats['beneficiarios'] += 1
                    
                    # =================== INSTITUIÇÃO ===================
                    # Usar instituição de destino como principal
                    nome_instituicao = str(row.get('INSTITUICAO_DESTINO', '')).strip()
                    sigla_instituicao = str(row.get('SIGLA_INSTITUICAO_DESTINO', '')).strip()
                    cidade = str(row.get('CIDADE_DESTINO', '')).strip()
                    uf = str(row.get('SIGLA_UF_DESTINO', '')).strip()
                    pais = str(row.get('PAIS_DESTINO', 'BRA - Brasil')).strip()
                    
                    # Chave única para instituição
                    instituicao_key = f"{nome_instituicao}_{sigla_instituicao}_{uf}"
                    
                    if nome_instituicao and instituicao_key not in instituicoes_cache:
                        instituicao = Instituicao(
                            nome=nome_instituicao,
                            sigla=sigla_instituicao,
                            cidade=cidade,
                            uf=uf,
                            pais=pais
                        )
                        db.add(instituicao)
                        db.flush()
                        instituicoes_cache[instituicao_key] = instituicao.id
                        stats['instituicoes'] += 1
                    
                    # =================== PROGRAMA ===================
                    nome_chamada = str(row.get('NOME_CHAMADA', '')).strip()
                    programa_cnpq = str(row.get('PROGRAMA_CNPQ', '')).strip()
                    grande_area = str(row.get('GRANDE_AREA', '')).strip()
                    area = str(row.get('AREA', '')).strip()
                    subarea = str(row.get('SUBAREA', '')).strip()
                    
                    # Chave única para programa
                    programa_key = f"{programa_cnpq}_{grande_area}_{area}"
                    
                    if programa_cnpq and programa_key not in programas_cache:
                        programa = Programa(
                            nome_chamada=nome_chamada,
                            programa_cnpq=programa_cnpq,
                            grande_area=grande_area,
                            area=area,
                            subarea=subarea
                        )
                        db.add(programa)
                        db.flush()
                        programas_cache[programa_key] = programa.id
                        stats['programas'] += 1
                    
                    # =================== PAGAMENTO ===================
                    if (cpf_anonimizado in beneficiarios_cache and 
                        instituicao_key in instituicoes_cache and 
                        programa_key in programas_cache):
                        
                        ano_referencia = int(row.get('ANO_REFERENCIA', 2024))
                        processo = str(row.get('PROCESSO', '')).strip()
                        modalidade = str(row.get('MODALIDADE', '')).strip()
                        linha_fomento = str(row.get('LINHA_FOMENTO', '')).strip()
                        valor_pago = parse_value(row.get('VALOR_PAGO', 0))
                        titulo_projeto = str(row.get('TITULO_PROJETO', '')).strip()
                        
                        # Datas
                        data_inicio = parse_date(row.get('DATA_INICIO_PROCESSO'))
                        data_fim = parse_date(row.get('DATA_TERMINO_PROCESSO'))
                        
                        pagamento = Pagamento(
                            ano_referencia=ano_referencia,
                            processo=processo,
                            modalidade=modalidade,
                            linha_fomento=linha_fomento,
                            valor_pago=valor_pago,
                            data_inicio=data_inicio,
                            data_fim=data_fim,
                            titulo_projeto=titulo_projeto,
                            fk_beneficiario=beneficiarios_cache[cpf_anonimizado],
                            fk_instituicao=instituicoes_cache[instituicao_key],
                            fk_programa=programas_cache[programa_key]
                        )
                        db.add(pagamento)
                        stats['pagamentos'] += 1
                    
                    stats['processadas'] += 1
                    
                    # Commit a cada 500 registros para performance
                    if index % 500 == 0 and index > 0:
                        db.commit()
                        print(f"  - Commit parcial: {index} registros processados")
                        
                except Exception as e:
                    print(f"Erro na linha {index}: {e}")
                    stats['erros'] += 1
                    continue
            
            # Commit final
            db.commit()
            
            print("\n" + "="*50)
            print("IMPORTAÇÃO CONCLUÍDA!")
            print("="*50)
            print(f"Total de linhas no CSV: {stats['total_linhas']}")
            print(f"Linhas processadas: {stats['processadas']}")
            print(f"Beneficiários únicos: {stats['beneficiarios']}")
            print(f"Instituições únicas: {stats['instituicoes']}")
            print(f"Programas únicos: {stats['programas']}")
            print(f"Pagamentos criados: {stats['pagamentos']}")
            print(f"Erros encontrados: {stats['erros']}")
            
            if stats['erros'] > 0:
                print(f"\nTaxa de erro: {(stats['erros']/stats['total_linhas'])*100:.2f}%")
            
        except Exception as e:
            print(f"Erro durante importação: {e}")
            db.rollback()
        finally:
            db.close()
            
    except Exception as e:
        print(f"Erro ao ler arquivo CSV: {e}")

def create_sample_data():
    """
    Cria dados de exemplo se não tiver CSV
    """
    print("Criando dados de exemplo...")
    
    # Criar tabelas
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Limpar dados existentes
        db.query(Pagamento).delete()
        db.query(Beneficiario).delete()
        db.query(Instituicao).delete()
        db.query(Programa).delete()
        db.commit()
        
        # Dados de exemplo baseados no CSV real
        instituicoes = [
            Instituicao(nome="Universidade Federal de Minas Gerais", sigla="UFMG", cidade="Belo Horizonte", uf="MG", pais="BRA - Brasil"),
            Instituicao(nome="Universidade do Estado do Rio de Janeiro", sigla="UERJ", cidade="Rio de Janeiro", uf="RJ", pais="BRA - Brasil"),
            Instituicao(nome="Universidade Federal do Rio Grande do Sul", sigla="UFRGS", cidade="Porto Alegre", uf="RS", pais="BRA - Brasil"),
            Instituicao(nome="Instituto Federal do Maranhao", sigla="IFMA", cidade="Sao Luis", uf="MA", pais="BRA - Brasil"),
            Instituicao(nome="Fundacao Oswaldo Cruz", sigla="FIOCRUZ", cidade="Rio de Janeiro", uf="RJ", pais="BRA - Brasil")
        ]
        
        for inst in instituicoes:
            db.add(inst)
        db.commit()
        
        programas = [
            Programa(nome_chamada="PQ - 2022", programa_cnpq="Programa Regular de Bolsas de Produtividade em Pesquisa", grande_area="Ciências Sociais Aplicadas", area="Serviço Social", subarea="Fundamentos do Serviço Social"),
            Programa(nome_chamada="PIBIC - 2024", programa_cnpq="Programa Institucional de Bolsas de Iniciação Científica - PIBIC", grande_area="Ciências Biológicas", area="Parasitologia", subarea="Protozoologia de Parasitos"),
            Programa(nome_chamada="IC JUNIOR - 2022", programa_cnpq="Programa de Iniciação Científica Júnior - ICJ-FAPs", grande_area="Engenharias", area="Tecnologias para o Desenvolvimento Sustentável", subarea="Não informado"),
            Programa(nome_chamada="ICMBIO 2022", programa_cnpq="PROGRAMA DE BIODIVERSIDADE", grande_area="Ciências Exatas e da Terra", area="Ciências Ambientais", subarea="Não informado"),
            Programa(nome_chamada="PIBITI - 2022", programa_cnpq="Programa Institucional de Bolsas de Iniciação em Desenv. Tecnológico e Inovação - PIBITI", grande_area="Ciências Agrárias", area="Agronomia", subarea="Ciência do Solo")
        ]
        
        for prog in programas:
            db.add(prog)
        db.commit()
        
        beneficiarios = [
            Beneficiario(nome="Silene de Moraes Freire", cpf_anonimizado="***.487.597-**", categoria_nivel="1C"),
            Beneficiario(nome="Amelia T Henriques", cpf_anonimizado="***.749.034-**", categoria_nivel="1A"),
            Beneficiario(nome="Victor Lucas Duarte Armani", cpf_anonimizado="***.178.986-**", categoria_nivel=""),
            Beneficiario(nome="Laís da Rocha Fernandes", cpf_anonimizado="***.499.832-**", categoria_nivel="B"),
            Beneficiario(nome="Sabrina Santana Borralho Araújo", cpf_anonimizado="***.636.733-**", categoria_nivel="")
        ]
        
        for benef in beneficiarios:
            db.add(benef)
        db.commit()
        
        # Pagamentos baseados nos dados reais
        pagamentos = [
            Pagamento(ano_referencia=2024, processo="306039/2022-2", modalidade="PQ - Produtividade em Pesquisa", linha_fomento="BOLSAS DE FORMAÇÃO E DE PESQUISADORES", valor_pago=5240.00, data_inicio=datetime(2023, 3, 1).date(), data_fim=datetime(2027, 7, 31).date(), titulo_projeto="Mídia Hegemônica e Descaminhos da Segurança Pública no Brasil", fk_beneficiario=1, fk_instituicao=2, fk_programa=1),
            Pagamento(ano_referencia=2024, processo="306892/2019-7", modalidade="PQ - Produtividade em Pesquisa", linha_fomento="BOLSAS DE FORMAÇÃO E DE PESQUISADORES", valor_pago=6120.00, data_inicio=datetime(2020, 3, 1).date(), data_fim=datetime(2025, 7, 31).date(), titulo_projeto="Busca de compostos bioativos relacionados a neurodegeneração", fk_beneficiario=2, fk_instituicao=3, fk_programa=1),
            Pagamento(ano_referencia=2024, processo="134373/2024-3", modalidade="IC - Iniciação Científica", linha_fomento="BOLSAS DE FORMAÇÃO E DE PESQUISADORES", valor_pago=2100.00, data_inicio=datetime(2024, 9, 1).date(), data_fim=datetime(2025, 8, 31).date(), titulo_projeto="", fk_beneficiario=3, fk_instituicao=1, fk_programa=2),
            Pagamento(ano_referencia=2024, processo="384815/2023-5", modalidade="DTI - Desenvolvimento Tecnológico Industrial", linha_fomento="APOIO A PROJETOS DE PESQUISA", valor_pago=11700.00, data_inicio=datetime(2023, 11, 1).date(), data_fim=datetime(2026, 3, 31).date(), titulo_projeto="Estratégias de conservação e monitoramento da biodiversidade aquática continental no Brasil", fk_beneficiario=4, fk_instituicao=1, fk_programa=4),
            Pagamento(ano_referencia=2024, processo="142382/2023-0", modalidade="ICJ - Iniciação Científica Júnior", linha_fomento="BOLSAS DE FORMAÇÃO E DE PESQUISADORES", valor_pago=600.00, data_inicio=datetime(2023, 9, 1).date(), data_fim=datetime(2024, 8, 31).date(), titulo_projeto="PIBIC EM/JR 2022/2024", fk_beneficiario=5, fk_instituicao=4, fk_programa=3)
        ]
        
        for pag in pagamentos:
            db.add(pag)
        db.commit()
        
        print("Dados de exemplo criados com sucesso!")
        print(f"- {len(instituicoes)} instituições")
        print(f"- {len(programas)} programas")
        print(f"- {len(beneficiarios)} beneficiários")
        print(f"- {len(pagamentos)} pagamentos")
        
    except Exception as e:
        print(f"Erro ao criar dados de exemplo: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    """Função principal"""
    print("Script de Importação de Dados CNPq")
    print("=" * 40)
    
    if len(sys.argv) > 1:
        # Se passou arquivo CSV como argumento
        csv_file = sys.argv[1]
        import_from_csv(csv_file)
    else:
        # Se não passou arquivo, criar dados de exemplo
        print("Nenhum arquivo CSV especificado.")
        print("Criando dados de exemplo para teste...")
        create_sample_data()
        
        print("\nPara importar dados reais do CNPq:")
        print("   python import_cnpq_data.py caminho/para/arquivo.csv")
        print("\nO arquivo CSV deve ter separador de tabulação (\\t)")

if __name__ == "__main__":
    main()