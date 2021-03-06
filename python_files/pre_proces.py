import numpy as np
import pandas as pd
import datetime
import Levenshtein

from otimizacao import *


def delete_wrong_dates(df_atual):
    print('Excluindo datas bsurdas')
    df_atual.idadeCaso = df_atual.idadeCaso.replace(range(101,1001), float("nan"))
    df_atual.loc[df_atual['idadeCaso'] == float("nan"), 'faixaEtaria'] = 'Sem Informacao'
    df_atual.faixaEtaria = df_atual.faixaEtaria.fillna('Sem Informacao')
    dates = ['dataResultadoExame', 'dataInicioSintomas', 'dataColetaExame']
    optimize2(df_atual, dates)
    return df_atual


def remove_columns(df_atual):
    print('Removendo colunas desnecessarias')
    df_atual = df_atual.drop(columns=['idRedcap', 'classificacaoEstadoRedcap', 'idEsus', 'idSivep',
                                'bairroCasoGeocoder', 'tipoObitoMaterno', 'codigoMunicipioCaso', 
                                'comorbidadeHiv', 'comorbidadeNeoplasias', 'paisCaso', 'estadoCaso',
                                'dataNascimento', 'requisicaoGal', 'laboratorioExame', 'cnesNotificacaoEsus',
                                'municipioNotificacaoEsus', 'localObito', 'comorbidadePuerperaSivep',
                                'comorbidadeHematologiaSivep', 'comorbidadeSindromeDownSivep',
                                'comorbidadeHepaticaSivep', 'comorbidadeNeurologiaSivep',
                                'comorbidadeImunodeficienciaSivep','comorbidadeRenalSivep', 
                                'comorbidadeObesidadeSivep', 'gestante', 'classificacaoEstadoEsus', 
                                'classificacaoFinalEsus', 'tipoTesteEsus', 'tipoLocalObito', 'classificacaoObito',
                                'evolucaoCasoEsus', 'evolucaoCasoSivep', 'tipoTesteExame',
                                'comorbidadeCardiovascularSivep',  'comorbidadeAsmaSivep', 'comorbidadeDiabetesSivep', 
                                'comorbidadePneumopatiaSivep', 'classificacaoEstadoSivep', 'dataNotificacao', 'dataSolicitacaoExame',
                                'dataInternacaoSivep', 'dataEntradaUTISivep', 'dataSaidaUTISivep', 'dataEvolucaoCasoSivep',
                                'dataNotificacaoObito', 'classificacaoFinalCasoSivep', 'racaCor'])
    return df_atual

def correct_cboEsus(df_atual):
    print("Corrigindo profiss??es")
    for i in df_atual.cboEsus.value_counts().index.to_list():
        correcao = i.split('-')[1]
        if correcao[0] == ' ':
            correcao = correcao[1:]
        df_atual.cboEsus.replace(i, correcao, inplace=True)
    return df_atual

def filter_muni(df_atual):
    print('Filtrando dados para Fortaleza')
    correcoes = {}
    for i in df_atual.municipioCaso.value_counts().index:
        lev = Levenshtein.distance(i,'FORTALEZA')
        if lev < 4:
            correcoes[i] = 'FORTALEZA'
            dist = lev
    for i in range(len(list(correcoes))):
        df_atual.municipioCaso = df_atual.municipioCaso.replace(list(correcoes)[i], correcoes[list(correcoes)[i]])

    filtro = (df_atual.municipioCaso == 'FORTALEZA')
    df_atual = df_atual[filtro]
    df_atual = df_atual.drop(columns=['municipioCaso'])
    return df_atual


def date_correction(df_atual):
    print('Corrigindo datas')
    anoDeCont = []
    dataCaso = []
    result = df_atual.dataResultadoExame.to_list()
    sintomas = df_atual.dataInicioSintomas.to_list()
    exame = df_atual.dataColetaExame.to_list()

    for i in range(len(result)):
        if sintomas[i].year == 2020:
            anoDeCont.append('2020')
            dataCaso.append(sintomas[i])
        elif sintomas[i].year == 2021:
            anoDeCont.append('2021')
            dataCaso.append(sintomas[i])
        else:
            if exame[i].year == 2020:
                anoDeCont.append('2020')
                dataCaso.append(exame[i])
            elif exame[i].year == 2021:
                anoDeCont.append('2021')
                dataCaso.append(exame[i])
            else:
                if result[i].year == 2020:
                    anoDeCont.append('2020')
                    dataCaso.append(result[i])
                elif result[i].year == 2021:
                    anoDeCont.append('2021')
                    dataCaso.append(result[i])
                else:
                    anoDeCont.append('Excluir')
                    dataCaso.append('Excluir')
    df_atual['anoDeContagio'] = anoDeCont

    for i in df_atual.columns.to_list(): 
        if i[0]+i[1]+i[2]+i[3] == 'data':
            df_atual = df_atual.drop(columns=i)
    df_atual['dataCaso'] = dataCaso

    indexNames = df_atual[ (df_atual['dataCaso'] == 'Excluir') |
                            (df_atual['anoDeContagio'] == 'Excluir') ].index
    df_atual.drop(indexNames , inplace=True)
    df_atual.drop(columns=['anoDeContagio'] , inplace=True)

    return df_atual


def wrong_values(df_atual):
    print('Tratando valores errados')

    df_atual.bairroCaso.fillna('Indeterminado', inplace=True)

    df_atual.sexoCaso.replace('INDEFINIDO', df_atual.sexoCaso.value_counts().index[0], inplace=True)
    df_atual.sexoCaso.replace('I', df_atual.sexoCaso.value_counts().index[0], inplace=True)
    df_atual.sexoCaso.replace('N.I.', df_atual.sexoCaso.value_counts().index[0], inplace=True)
    df_atual.sexoCaso.fillna(df_atual.sexoCaso.value_counts().index[0], inplace=True)

    df_atual.resultadoFinalExame.replace('Prov??vel', 'Caso suspeito', inplace=True)
    df_atual.resultadoFinalExame.replace('Inconclusivo', 'Caso suspeito', inplace=True)
    df_atual.resultadoFinalExame.replace('Em An??lise', 'Caso suspeito', inplace=True)
    df_atual.resultadoFinalExame.fillna('Caso suspeito', inplace=True)
    # df_atual.resultadoFinalExame.replace('Negativo', 'Z Negativo', inplace=True)

    # df_atual.racaCor.replace('Parda.0', 'Parda', inplace=True)
    # df_atual.racaCor.replace('.0', 'Sem Informacao', inplace=True)
    # df_atual.racaCor.fillna('Sem Informacao', inplace=True)
    # df_atual.racaCor.replace('Branca.0', 'Branca', inplace=True)
    # df_atual.racaCor.replace('Preta.0', 'Preta', inplace=True)
    # df_atual.racaCor.replace('Amarela.0', 'Amarela', inplace=True)
    # df_atual.racaCor.replace('Ind??gena.0', 'Ind??gena', inplace=True)

    df_atual.obitoConfirmado.replace(True, 'Verdadeiro', inplace=True)
    df_atual.obitoConfirmado.replace(False, 'Falso', inplace=True)
    df_atual.obitoConfirmado.fillna('Falso', inplace=True)

    return df_atual


def correction_bairro(df_atual, bairro_info):
    print('Corrigindo bairros')
    correcoes = {}
    bairros_cor = bairro_info.index
    for i in df_atual.bairroCaso.value_counts().index:
        dist = 20
        for j in bairros_cor:
            lev = Levenshtein.distance(i,j)
            if dist == 20 and lev < 3:
                correcoes[i] = j
                dist = lev
            elif dist < 20 and lev < dist:
                correcoes[i] = j
                dist = lev

    for i in range(len(list(correcoes))):
        df_atual.bairroCaso = df_atual.bairroCaso.replace(list(correcoes)[i], correcoes[list(correcoes)[i]])

    filtro = ~ df_atual.bairroCaso.isin(bairros_cor)
    df_atual.loc[filtro, 'bairroCaso'] = 'Indeterminado'

    return df_atual


def prof_group(df_atual):
    print('Criando grupos')
    dicGrupo = {'T??cnicos e auxiliares de enfermagem' : 'Profissional da saude',
        'Enfermeiros e afins' : 'Profissional da saude',
        'M??dico' : 'Profissional da saude',
        'Agente Comunit??rio de Sa??de' : 'Profissional da saude',
        'Farmac??uticos' : 'Profissional da saude',
        'Fisioterapeutas' : 'Profissional da saude',
        'Cirurgi??o' : 'Profissional da saude',
        'Psic??logos e psicanalistas' : 'Profissional da saude',
        'Cuidador em Sa??de' : 'Profissional da saude',
        'M??dicos cl??nicos' : 'Profissional da saude',
        'Nutricionistas' : 'Profissional da saude',
        'Policiais' : 'Policial/Exercito/Bombeiros',
        'Outro tipo de agente de sa??de ou visitador sanit??rio' : 'Profissional da saude',
        'Agente de Sa??de P??blica' : 'Profissional da saude',
        'Profissionais da educa????o f??sica' : 'Profissionais da Educa????o',
        'Vigilantes e guardas de seguran??a' : 'Policial/Exercito/Bombeiros',
        'M??dicos em medicina diagn??stica e terap??utica' : 'Profissional da saude',
        'Terapeutas ocupacionais' : 'Profissional da saude',
        'Condutor de Ambul??ncia' : 'Profissional da saude',
        'Cabos e soldados da pol??cia militar' : 'Policial/Exercito/Bombeiros',
        'Oficiais generais das for??as armadas' : 'Policial/Exercito/Bombeiros',
        'T??cnicos de odontologia' : 'Profissional da saude',
        'Professor de Educa????o Infantil ou Ensino Fundamental' : 'Profissionais da Educa????o',
        'Socorrista n??o m??dico e n??o enfermeiro' : 'Profissional da saude',
        'T??cnico em farm??cia e em manipula????o farmac??utica' : 'Profissional da saude',
        'Engenheiros civis e afins' : 'Profissionais da ??rea de constru????o',
        'Inspetores de alunos e afins' : 'Profissionais da Educa????o',
        'Biom??dico' : 'Profissional da saude',
        'Professor do Ensino M??dio' : 'Profissionais da Educa????o',
        'Subtenentes e sargentos da policia militar' : 'Policial/Exercito/Bombeiros',
        'Cozinheiros' : 'Profissionais da ??rea aliment??cia',
        'Profissional da Biotecnologia' : 'Profissional da saude',
        'T??cnicos em transportes a??reos' : 'Transporte',
        'Contadores e afins' : 'Finan??as e Secretariado',
        'Operadores de m??quinas para costura de pe??as do vestu??rio' : 'Industria textil',
        'Outros profissionais de ensino' : 'Profissionais da Educa????o',
        'Dirigentes do servi??o p??blico' : 'Finan??as e Secretariado',
        'Motoristas de ve??culos de cargas em geral' : 'Transporte ',
        'Secret??rias(os) executivas(os) e afins' : 'Finan??as e Secretariado',
        'Auxiliares de servi??os de documenta????o' : 'Finan??as e Secretariado',
        'Lavadores e passadores de roupa' : 'Industria textil',
        'Professor de Ensino Superior' : 'Profissionais da Educa????o',
        'Trabalhadores no atendimento em estabelecimentos de servi??os de alimenta????o' : 'Profissionais da ??rea aliment??cia',
        'Trabalhadores nos  servi??os de manuten????o de edifica????es' : 'Profissionais da ??rea de constru????o',
        'Oficiais superiores da pol??cia militar' : 'Policial/Exercito/Bombeiros',
        'Arquitetos e urbanistas' : 'Profissionais da ??rea de constru????o',
        'Assistentes sociais e economistas dom??sticos' : 'Finan??as e Secretariado',
        'Motociclistas e ciclistas de entregas r??pidas' : 'Profissionais da ??rea aliment??cia',
        'Trabalhadores auxiliares nos servi??os de alimenta????o' : 'Profissionais da ??rea aliment??cia',
        'Delegados de pol??cia' : 'Policial/Exercito/Bombeiros',
        'Profissionais de administra????o ec??nomico' : 'Finan??as e Secretariado',
        'T??cnicos em constru????o civil (edifica????es)' : 'Profissionais da ??rea de constru????o',
        'Bombeiros' : 'Policial/Exercito/Bombeiros',
        'Diretores administrativos e financeiros' : 'Finan??as e Secretariado',
        'T??cnico em Eletroeletr??nica e Fot??nica atuando na ??rea de sa??de' : 'T.I., Tecnologias e mecanica',
        'Tenentes da pol??cia militar' : 'Policial/Exercito/Bombeiros',
        'Motoristas de ??nibus urbanos' : 'Transporte',
        'Gerentes de tecnologia da informa????o' : 'T.I., Tecnologias e mecanica',
        'Auxiliares de contabilidade' : 'Finan??as e Secretariado',
        'Capit??es da  pol??cia militar' : 'Policial/Exercito/Bombeiros',
        'Ajudantes de obras civis' : 'Profissionais da ??rea de constru????o',
        'T??cnicos mec??nicos (ferramentas)' : 'T.I., Tecnologias e mecanica',
        'M??dicos em especialidades cir??rgicas' : 'Profissional da saude',
        'Profissionais polivalentes da confec????o de roupas' : 'Industria textil',
        'Chefes de cozinha e afins' : 'Profissionais da ??rea aliment??cia',
        'Professores de n??vel superior na educa????o infantil' : 'Profissionais da Educa????o',
        'Eletricistas de manuten????o eletroeletr??nica' : 'T.I., Tecnologias e mecanica',
        'T??cnicos em contabilidade' : 'Finan??as e Secretariado',
        'Professores de n??vel m??dio na educa????o infantil' : 'Profissionais da Educa????o',
        'Diretores e gerentes de institui????o de servi??os educacionais' : 'Profissionais da Educa????o',
        'T??cnicos em opera????es e servi??os banc??rios' : 'Finan??as e Secretariado',
        'Padeiros' : 'Profissionais da ??rea aliment??cia',
        'Profissionais da informa????o' : 'T.I., Tecnologias e mecanica',
        'T??cnicos em constru????o civil (obras de infraestrutura)' : 'Profissionais da ??rea de constru????o',
        'Trabalhadores em registros e informa????es em sa??de' : 'T.I., Tecnologias e mecanica',
        'Cabos e soldados do corpo de bombeiros militar' : 'Policial/Exercito/Bombeiros',
        'T??cnicos em eletr??nica' : 'T.I., Tecnologias e mecanica',
        'Professores do ensino m??dio' : 'Profissionais da Educa????o',
        'Trabalhadores de seguran??a e atendimento aos usu??rios nos transportes' : 'Transporte',
        'Engenheiros eletricistas' : 'T.I., Tecnologias e mecanica',
        'Supervisores de servi??os financeiros' : 'Finan??as e Secretariado',
        'Operadores de m??quinas de costurar e montar cal??ados' : 'Industria textil',
        'Supervisores de lavanderia' : 'Industria textil',
        'Pintores de obras e revestidores de interiores (revestimentos flex??veis)' : 'Profissionais da ??rea de constru????o',
        'Administradores de tecnologia da informa????o' : 'T.I., Tecnologias e mecanica',
        'Professores de n??vel superior do ensino fundamental (primeira a quarta s??ries)' : 'Profissionais da Educa????o',
        'Profissionais de direitos autorais e de avaliac??o de produtos dos meios de comunica????o' : '',
        'Oficiais de m??quinas da marinha mercante' : 'Policial/Exercito/Bombeiros',
        'Programadores' : 'T.I., Tecnologias e mecanica',
        'Professores na ??rea de forma????o pedag??gica do ensino superior' : 'Profissionais da Educa????o',
        'Professores de n??vel m??dio no ensino fundamental' : 'Profissionais da Educa????o',
        'T??cnicos em secretariado' : 'Finan??as e Secretariado',
        'Designers de interiores' : 'Profissionais da ??rea de constru????o',
        'Engenheiro de Alimentos' : 'Profissionais da ??rea aliment??cia',
        'Economistas' : 'Finan??as e Secretariado',
        'T??cnicos em eletricidade e eletrot??cnica' : 'T.I., Tecnologias e mecanica',
        'Engenheiros mec??nicos e afins' : 'T.I., Tecnologias e mecanica',
        'Professor de Ensino Profissionalizante' : 'Profissionais da Educa????o',
        'Oficiais intermedi??rios do corpo de bombeiros militar' : 'Policial/Exercito/Bombeiros',
        'Trabalhadores da prepara????o da confec????o de roupas' : 'Industria textil',
        'Diretores de opera????es de servi??os em institui????o de intermedia????o financeira' : 'Finan??as e Secretariado',
        'Supervisores da constru????o civil' : 'Profissionais da ??rea de constru????o',
        'Gerentes de opera????es de servi??os em empresa de transporte' : 'Transporte',
        'Professores de educa????o especial' : 'Profissionais da Educa????o',
        'Supervisores na confec????o do vestu??rio' : 'Industria textil',
        'Supervisores dos servi??os de transporte' : 'Transporte',
        'Mec??nicos de manuten????o de bombas' : 'T.I., Tecnologias e mecanica',
        'Trabalhadores de instala????es el??tricas' : 'Profissionais da ??rea de constru????o',
        'Mec??nicos de manuten????o de ve??culos automotores' : 'T.I., Tecnologias e mecanica',
        'T??cnicos de suporte e monitora????o ao usu??rio de tecnologia da informa????o.' : 'T.I., Tecnologias e mecanica',
        'Subtenentes e sargentos do corpo de bombeiros militar' : 'Policial/Exercito/Bombeiros',
        'Professores leigos no ensino fundamental' : 'Profissionais da Educa????o',
        'T??cnicos em manuten????o e repara????o de equipamentos biom??dicos' : 'T.I., Tecnologias e mecanica',
        'Pesquisadores de engenharia e tecnologia' : 'T.I., Tecnologias e mecanica',
        'Trabalhadores artesanais da confec????o de pe??as e tecidos' : 'Industria textil',
        'Instrutores e professores de cursos livres' : 'Profissionais da Educa????o',
        'Oficiais superiores do corpo de bombeiros militar' : 'Policial/Exercito/Bombeiros',
        'Trabalhadores da fabrica????o de cer??mica estrutural para constru????o' : 'Profissionais da ??rea de constru????o',
        'Engenheiros em computa????o' : 'T.I., Tecnologias e mecanica',
        'Supervisores da fabrica????o de alimentos' : 'Profissionais da ??rea aliment??cia',
        'T??cnicos em telecomunica????es' : 'T.I., Tecnologias e mecanica',
        'Mec??nicos de manuten????o aeron??utica' : 'T.I., Tecnologias e mecanica',
        'Professores de n??vel superior no ensino fundamental de quinta a oitava s??rie' : 'Profissionais da Educa????o',
        'Desenhistas projetistas de constru????o civil e arquitetura' : 'Profissionais da ??rea de constru????o',
        'Supervisores da ind??stria t??xtil' : 'Industria textil',
        'Trabalhadores de acabamento de cal??ados' : 'Industria textil',
        'Pilotos de avia????o comercial' : 'Transporte',
        'Mec??nicos de instrumentos de precis??o' : 'T.I., Tecnologias e mecanica',
        'Trabalhadores agropecu??rios em geral' : 'Profissionais da ??rea aliment??cia',
        'Inspetores e revisores de produ????o t??xtil' : 'Industria textil',
        'Instaladores e mantenedores de sistemas eletroeletr??nicos de seguran??a' : 'T.I., Tecnologias e mecanica',
        'Operadores de tear e m??quinas similares' : 'Industria textil',
        'Aplicadores de revestimentos cer??micos' : 'Profissionais da ??rea de constru????o',
        'T??cnicos mec??nicos na manuten????o de m??quinas' : 'T.I., Tecnologias e mecanica',
        'Professores de artes do ensino superior' : 'Profissionais da Educa????o',
        'T??cnicos do vestu??rio' : 'Industria textil',
        'Supervisores de manuten????o eletromec??nica' : 'T.I., Tecnologias e mecanica',
        'Vidreiros e ceramistas (arte e decora????o)' : 'Profissionais da ??rea de constru????o',
        'Gerentes de obras em empresa de constru????o' : 'Profissionais da ??rea de constru????o',
        'Trabalhadores de tecelagem manual' : 'Industria textil',
        'Professores do ensino profissional' : 'Profissionais da Educa????o',
        'Gerentes operacionais da avia????o civil' : 'Transporte',
        'Trabalhadores polivalentes das ind??strias t??xteis' : 'Industria textil',
        'Gerentes de opera????es de servi??os em institui????o de intermedia????o financeira' : 'Finan??as e Secretariado',
        'Tenentes do corpo de bombeiros militar' : 'Policial/Exercito/Bombeiros'}

    for i in range(len(list(dicGrupo))):
        df_atual.loc[df_atual.cboEsus == list(dicGrupo)[i], 'profissoes'] = dicGrupo[list(dicGrupo)[i]]

    df_atual.drop(columns=['cboEsus'], inplace=True)
    return df_atual


def processing_new_rows(df_atual):
    df_atual = remove_columns(df_atual)
    df_atual = delete_wrong_dates(df_atual)
    df_atual = correct_cboEsus(df_atual)
    df_atual = filter_muni(df_atual)
    df_atual = date_correction(df_atual)
    df_atual = wrong_values(df_atual)

    bairro_info = pd.read_csv(f'Base_de_dados/dados_bairros.csv', sep=',')
    bairro_info.Bairros	= bairro_info.Bairros.str.upper()
    bairro_info = bairro_info.set_index('Bairros')

    df_atual = correction_bairro(df_atual, bairro_info)
    df_atual = prof_group(df_atual)

    # df_atual.sort_values(by=['resultadoFinalExame'], inplace=True)  
    # df_atual.drop_duplicates(subset='identificadorCaso', keep='last', inplace=True)
    # df_atual = df_atual.drop(columns=['identificadorCaso'])


    df_atual.to_csv('base_de_dados/dados_limpos.csv', sep=';')
    

    

