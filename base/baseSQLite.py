
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 30 23:22:16 2024

@author: ILIA
"""
import sqlite3 as sq

path_base = 'base/base.sqlite'
sql_statements = [
        """CREATE TABLE IF NOT EXISTS LOKO_TYPE (
                id INTEGER NOT NULL,
                "name" TEXT NOT NULL,
                PRIMARY KEY(id)
        );""",
        """CREATE TABLE IF NOT EXISTS LOKO_PADS (
                id INTEGER NOT NULL,
                "name" TEXT NOT NULL,
                PRIMARY KEY(id)
        );""",
        """CREATE TABLE IF NOT EXISTS LOKO (
                id INTEGER NOT NULL,
                "name" TEXT NOT NULL,
                "type" INTEGER NOT NULL,
                "pads" INTEGER NOT NULL,
                "axles" INTEGER NOT NULL,
                "weight" REAL NOT NULL,
                "force" REAL NOT NULL,
                "desc" TEXT,
                "URL" TEXT,
                PRIMARY KEY(id),
                FOREIGN KEY (type) REFERENCES LOKO_TYPE (ID),
                FOREIGN KEY (pads) REFERENCES LOKO_PADS (ID)
        );""",
        """CREATE TABLE IF NOT EXISTS VAGON_TYPE (
                id INTEGER NOT NULL,
                "name" TEXT NOT NULL,
                PRIMARY KEY(id)
        );""",
        """CREATE TABLE IF NOT EXISTS VAGON (
                id INTEGER NOT NULL,
                "name" TEXT NOT NULL,
                "type" INTEGER NOT NULL,
                "force" REAL NOT NULL,
                PRIMARY KEY(id),
                FOREIGN KEY (type) REFERENCES VAGON_TYPE (ID)
        );"""
    ]

def get_conn_to_base():
    conn = sq.connect(path_base)
    conn.execute("PRAGMA foreign_keys = 1")
    cursor = conn.cursor()
    for statement in sql_statements:
       cursor.execute(statement)
    conn.commit()
    return conn

if __name__=='__main__':
    pass