"""Cloud related classes"""
import uuid

import mongoengine as me


class CloudLocation(me.Document):
    """A base Cloud Location Model."""
    id = me.StringField(primary_key=True, default=lambda: uuid.uuid4().hex)
    cloud = me.ReferenceField('Cloud', required=True)
    location_id = me.StringField(required=True)
    provider = me.StringField()
    name = me.StringField()
    country = me.StringField()

    meta = {
        'collection': 'cloud_locations',
        'indexes': [
            {
                'fields': ['cloud', 'location_id'],
                'sparse': False,
                'unique': True,
                'cls': False,
            },
        ],
        'strict': False,
    }

    def __str__(self):
        name = "%s, %s (%s)" % (self.name, self.provider, self.location_id)
        return name

    def as_dict(self):
        return {
            'id': self.location_id,
            'cloud': self.cloud.id,
            'provider': self.provider,
            '_id': self.id,
            'name': self.name,
            'country': self.country,
        }


class CloudImage(me.Document):
    """A base Cloud Image Model."""
    image_id = me.StringField(required=True)
    cloud_provider = me.StringField(required=True)
    cloud_region = me.StringField()  # eg for RackSpace
    name = me.StringField()
    os_type = me.StringField(default='linux')
    deprecated = me.BooleanField(default=False)

    meta = {
        'indexes': [
            'cloud_provider',
            'image_id',
            {
                'fields': ['cloud_provider', 'cloud_region', 'image_id'],
                'sparse': False,
                'unique': True,
                'cls': False,
            },
        ],
    }

    def __str__(self):
        name = "%s, %s (%s)" % (self.name, self.cloud_provider, self.image_id)
        return name

    def clean(self):
        # os_type is needed for the pricing per VM
        if self.name and self.cloud_provider.startswith('ec2'):
            if 'suse linux enterprise' or 'sles' in self.name.lower():
                self.os_type = 'sles'
            if 'red hat' or 'rhel' in self.name.lower():
                self.os_type = 'rhel'
            if 'windows' in self.name.lower():
                self.os_type = 'mswin'
                if 'sql' in self.name.lower():
                    self.os_type = 'mswinSQL'
                    if 'web' in self.name.lower():
                        self.os_type = 'mswinSQLWeb'
            if 'vyatta' in self.name.lower():
                self.os_type = 'vyatta'
        if self.name and self.cloud_provider.startswith('rackspace'):
            if 'red hat' in self.name.lower():
                self.os_type = 'redhat'
            if 'windows server' in self.name.lower():
                self.os_type = 'windows'
                if 'sql' in self.name.lower():
                    self.os_type = 'mssql-standard'
                    if 'web' in self.name.lower():
                        self.os_type = 'mssql-web'
            if 'vyatta' in self.name.lower():
                self.os_type = 'vyatta'

        super(CloudImage, self).clean()


class CloudSize(me.Document):
    """A base Cloud Size Model."""
    id = me.StringField(primary_key=True, default=lambda: uuid.uuid4().hex)
    cloud = me.ReferenceField('Cloud', required=True)
    provider = me.StringField(required=True)
    size_id = me.StringField(required=True)
    description = me.StringField()
    name = me.StringField()
    cpus = me.IntField()
    ram = me.IntField()
    price = me.DecimalField()
    cloud_region = me.StringField()  # eg for RackSpace
    disk = me.IntField()
    bandwidth = me.IntField()

    def __init__(self, *args, **kwargs):
        super(CloudSize, self).__init__(*args, **kwargs)

    def __str__(self):
        name = "%s, %s (%s)" % (self.name, self.provider, self.size_id)
        return name

    def as_dict(self):
        return {
            'id': self.size_id,
            'provider': self.provider,
            '_id': self.id,
            'name': self.name,
            'cpus': self.cpus,
            'ram': self.ram,
            'bandwidth': self.bandwidth,
            'description': self.description,
            'price': self.price,
            'disk': self.disk,
            # 'cloud_region': self.cloud_region,
        }
