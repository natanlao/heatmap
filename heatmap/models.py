# -*- coding: utf-8 -*-
from peewee import *

db = SqliteDatabase('heatmap.db')
#db = SqliteDatabase(":memory:")

class Subnet(Model):
    comment = CharField(null=True)
    network = CharField()
    subnet  = CharField()
    gateway = CharField()

    class Meta:
        database = db

class Listing(Model):
    subnet = ForeignKeyField(Subnet, related_name="listings")
    fixed = IntegerField()
    pool = IntegerField()
    assigned = IntegerField()
    asof = DateTimeField()

    class Meta:
        database = db

