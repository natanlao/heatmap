# -*- coding: utf-8 -*-
from peewee import *

#db = SqliteDatabase('heatmap.db')
db = SqliteDatabase(":memory:")

class Subnet(Model):
    comment = CharField()
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
    #asof = DateTimeField(formats=["%a %b %d %H:%M:%S PST %Y"])
    asof = DateTimeField()

    class Meta:
        database = db

