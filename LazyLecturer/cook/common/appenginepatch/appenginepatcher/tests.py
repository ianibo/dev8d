# -*- coding: utf-8 -*-
from django.db.models import signals
from django.test import TestCase
from ragendja.dbutils import cleanup_relations
from ragendja.testutils import ModelTestCase
from google.appengine.ext import db
from google.appengine.ext.db.polymodel import PolyModel

# Test class Meta

class TestA(db.Model):
    class Meta:
        abstract = True
        verbose_name = 'aaa'

class TestB(TestA):
    class Meta:
        verbose_name = 'bbb'

class TestC(TestA):
    pass

class PolyA(PolyModel):
    class Meta:
        verbose_name = 'polyb'

class PolyB(PolyA):
    pass

class ModelMetaTest(TestCase):
    def test_class_meta(self):
        self.assertEqual(TestA._meta.verbose_name_plural, 'aaas')
        self.assertTrue(TestA._meta.abstract)

        self.assertEqual(TestB._meta.verbose_name_plural, 'bbbs')
        self.assertFalse(TestB._meta.abstract)

        self.assertEqual(TestC._meta.verbose_name_plural, 'test cs')
        self.assertFalse(TestC._meta.abstract)

        self.assertFalse(PolyA._meta.abstract)
        self.assertFalse(PolyB._meta.abstract)

# Test signals

class SignalTest(TestCase):
    def test_signals(self):
        global received
        received = False
        def handle_pre_delete(**kwargs):
            global received
            received = True
        signals.pre_delete.connect(handle_pre_delete, sender=TestC)
        a = TestC()
        a.put()
        a.delete()
        self.assertTrue(received)

# Test serialization

class SerializeModel(db.Model):
    name = db.StringProperty()
    count = db.IntegerProperty()

class SerializerTest(ModelTestCase):
    model = SerializeModel

    def test_serializer(self, format='json'):
        from django.core import serializers
        x = SerializeModel(key_name='blue_key', name='blue', count=4)
        x.put()
        SerializeModel(name='green', count=1).put()
        data = serializers.serialize(format, SerializeModel.all())
        db.delete(SerializeModel.all().fetch(100))
        for obj in serializers.deserialize(format, data):
            obj.save()
        self.validate_state(
            ('key.name', 'name',  'count'),
            (None,       'green', 1),
            ('blue_key', 'blue',  4),
        )

    def test_xml_serializer(self):
        self.test_serializer(format='xml')

    def test_python_serializer(self):
        self.test_serializer(format='python')

    def test_yaml_serializer(self):
        self.test_serializer(format='yaml')

# Test ragendja cleanup handler
class SigChild(db.Model):
    CLEANUP_REFERENCES = 'rel'

    owner = db.ReferenceProperty(TestC)
    rel = db.ReferenceProperty(TestC, collection_name='sigchildrel_set')

class RelationsCleanupTest(TestCase):
    def test_cleanup(self):
        signals.pre_delete.connect(cleanup_relations, sender=TestC)
        c1 = TestC()
        c2 = TestC()
        db.put((c1, c2))
        child = SigChild(owner=c1, rel=c2)
        child.put()
        self.assertEqual(TestC.all().count(), 2)
        self.assertEqual(SigChild.all().count(), 1)
        c1.delete()
        signals.pre_delete.disconnect(cleanup_relations, sender=TestC)
        self.assertEqual(SigChild.all().count(), 0)
        self.assertEqual(TestC.all().count(), 0)
