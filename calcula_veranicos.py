#!/usr/bin/env python3.6

# coding: utf-8

"""Este script calcula a probabilidade de se encontrar
verânicos com x dias de tamanho, dentro de uma série amostral.
"""

__author__ = 'Marcelo Rodrigues'
__email__ = 'marcelorodriguesss@gmail.com'
__date__ = '30 Jan 2018'

import numpy as np
import pandas as pd
import datetime

np.set_printoptions(precision=2, suppress=True, threshold=np.nan)


def compute_vrnc(df, n_vrn, trhld, idate, fdate):

    # define o período
    df = df.loc[idate:fdate]

    # print(df)

    # possibilidade de ter veranicos com 'x' tamanho (espaço amostral )
    # count() não conta com NaN
    sample_space = df['pr'] \
        .rolling(n_vrn, min_periods=n_vrn) \
        .sum().count()

    print('\n*** Espaço amostral: {}\n'.format(sample_space))

    # define como NaN valores menores que o limiar definido (trhld)
    # os valores com NaN serão os dias com chuva abaixo do limiar
    df = df.where(df['pr'] > trhld, np.nan)

    # encontra, define um id (group) e agrupa os verânicos de
    # tamanho 'x' (n_vrn)
    df['id_group'] = df.pr.notnull().astype(int).cumsum()
    df = df[df.pr.isnull()]
    df = df[df.id_group.isin(df.id_group.value_counts()
                          [df.id_group.value_counts() >= n_vrn]
                          .index)]
    df['vrn_size'] = df.groupby('id_group')['id_group'].transform('size')
    df.drop_duplicates(['id_group'], keep='first')

    # print('*** Verânicos Encotrados ***\n')
    # print(df)

    df = df.groupby('id_group').first()
    df = (df[df['vrn_size'] >= n_vrn])
    # print('\n*** Súmario dos resultados ***\n')
    # print(df)

    res = []
    for x in df['vrn_size'].values:
        if x == n_vrn:
            res.append(1)
        else:
            count = x // n_vrn
            res.append(count)
    res = np.sum(res)
    prob = (res / sample_space) * 100

    print('*** Tamanho do verânico....: {} dias'.format(n_vrn))
    print('*** Limiar diário..........: {} mm'.format(trhld))
    print('*** Verânicos encontrados..: {}'.format(res))

    return prob


if __name__ == "__main__":

    pr_file = '/home/rodrigues/gitlab-funceme/analise_obj_ons/' \
              'pr_daily_funceme_thiessen_19710101_20171231_ce.asc'

    df = pd.read_table(pr_file, header=None, sep=' ',
                       names=['ano', 'mes', 'dia', 'pr'])

    # define as colunas 'ano', 'mes' e 'dia' como datetime em
    # uma nova coluna nomeada como 'data'
    df['date'] = df[['ano', 'mes', 'dia']] \
        .apply(lambda x: datetime.datetime(*x), axis=1)

    # define a coluna data como índice do DataFrame (df)
    df.set_index(df['date'], inplace=True)

    # remove as colunas que não serão mais usadas
    df = df.drop(['ano', 'mes', 'dia', 'date'], axis=1)

    n_vrn = 3
    trhld = 2.0
    idate = '2009-02-01'
    fdate = '2009-06-30'

    prob = compute_vrnc(df, n_vrn, trhld, idate, fdate)

    print('*** Probabilidade..........: {:2.2f}%'.format(prob))
