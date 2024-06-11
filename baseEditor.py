# -*- coding: utf-8 -*-
"""
Created on Sat Jun  1 20:18:19 2024

@author: ILIA
"""
from views.ed_base import EditBase
from base.baseSQLite import get_conn_to_base

if __name__ == "__main__":
    cnx = get_conn_to_base()
    EditBase(cnx)
    cnx.close()