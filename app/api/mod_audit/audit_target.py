# -*- coding: utf-8 -*-
from app.api.mod_item.validate import can_user_modify_item
from app.api.mod_org.validate import can_user_modify_org
from app.api.mod_project.validate import can_user_modify_project
from app.api.models.audit import Audit
from app.api.models.base import Resource
from app.api.models.item import Item
from app.api.models.org import Org
from app.api.models.project import Project
from app.api.models.version import ResourceVersion
from app.api.utils.resource import get_resource_model
from app.exc import GulDanException


class AuditTarget(object):

    VERSION_ZERO = ResourceVersion(1, -1, 0, "", -1)

    def __init__(self, resource):
        self.resource = resource

    def get_audit_count(self):
        return Audit.get_audit_count_for_resource_id(self.resource.id)

    @staticmethod
    def get_version_dict(resource_id, resource_type, resource_version_ids):
        versions = ResourceVersion.get_versions_by_resource(resource_id, resource_type, resource_version_ids)
        versions_dict = {0: AuditTarget.VERSION_ZERO}
        for version in versions:
            versions_dict[version.version_id] = version

        return versions_dict

    @staticmethod
    def get_resource_current_version(resource_id, resource_type):
        resource_model = get_resource_model(resource_type)
        resource = resource_model.get_by_id(resource_id)
        if resource_type == Resource.Type.ITEM:
            resource_content = resource.data
            type_within_resource = resource.type
        else:
            resource_content = ""
            type_within_resource = 0

        return ResourceVersion(
            resource_id, resource_type, resource.current_version_id, resource_content, resource.visibility,
            type=type_within_resource
        )

    @staticmethod
    def generate_versions_list(resource_id, resource_type, audits):
        resource_version_ids = [audit.version_id for audit in audits]
        versions = ResourceVersion.get_versions_by_resource(resource_id, resource_type, resource_version_ids)
        versions.sort(key=lambda x: x.version_id, reverse=True)
        current_version = AuditTarget.get_resource_current_version(resource_id, resource_type)
        versions.append(current_version)

        return versions

    def version_type_to_str(self, version_type):
        raise NotImplementedError()

    def get_audits_for_resource(self, resource_id, resource_type, limit=100, offset=0):
        audits = Audit.get_audit_for_resource_id(resource_id, resource_type, limit=limit+1, offset=offset)
        if not audits:
            return []

        versions = AuditTarget.generate_versions_list(resource_id, resource_type, audits)

        for i in range(len(audits)-1):
            audit = audits[i]
            version = versions[i]
            last_version = versions[i + 1]

            audit.data = {
                "before": last_version.resource_content,
                "after": version.resource_content
            }
            audit.resource_visibility = {
                "before": Resource.Visibility.to_str(last_version.resource_visibility),
                "after": Resource.Visibility.to_str(version.resource_visibility)
            }
            audit.type = {
                "before": self.version_type_to_str(last_version.type),
                "after": self.version_type_to_str(version.type)
            }

        return audits[:-1]


class OrgAuditTarget(AuditTarget):
    def __init__(self, resource, user_hash):
        super(OrgAuditTarget, self).__init__(resource)
        self.user_hash = user_hash

    def can_view_audit(self):
        return can_user_modify_org(self.resource.id, self.user_hash)

    def version_type_to_str(self, version_type):
        return "org"

    def get_audit(self, offset=0, limit=100):
        return self.get_audits_for_resource(self.resource.id, Resource.Type.ORG, limit=limit, offset=offset)

    def get_audit_count(self):
        return Audit.get_audit_count_for_resource(self.resource.id, Resource.Type.ORG)


class ProjectAuditTarget(AuditTarget):
    def __init__(self, resource, user_hash):
        super(ProjectAuditTarget, self).__init__(resource)
        self.user_hash = user_hash

    def can_view_audit(self):
        return can_user_modify_project(self.resource.id, self.user_hash)

    def version_type_to_str(self, version_type):
        return "project"

    def get_audit(self, offset=0, limit=100):
        return self.get_audits_for_resource(self.resource.id, Resource.Type.PROJECT, limit=limit, offset=offset)

    def get_audit_count(self):
        return Audit.get_audit_count_for_resource(self.resource.id, Resource.Type.PROJECT)


class ItemAuditTarget(AuditTarget):
    def __init__(self, resource, user_hash):
        super(ItemAuditTarget, self).__init__(resource)
        self.user_hash = user_hash

    def can_view_audit(self):
        return can_user_modify_item(self.resource.id, self.user_hash)

    def version_type_to_str(self, version_type):
        return Item.Type.to_str(version_type)

    def get_audit(self, offset=0, limit=100):
        return self.get_audits_for_resource(self.resource.id, Resource.Type.ITEM, limit=limit, offset=offset)

    def get_audit_count(self):
        return Audit.get_audit_count_for_resource(self.resource.id, Resource.Type.ITEM)
    

class InvalidAuditTarget(object):
    def __init__(self, resource_name, user_hash):
        self.resource_name = resource_name
        self.user_hash = user_hash
        
    def can_view_audit(self):
        raise GulDanException().with_code(403).with_message(
            u"非法的审查对象, resource_name:{}".format(self.resource_name)
        )


def get_resource(resource_model, resource_name):
    resource = resource_model.get_by_name(resource_name)
    if not resource:
        raise GulDanException().with_code(404).with_message(
            u"找不到资源:{}".format(resource_name)
        )
    return resource


def generate_audit_target(resource_name, user_hash):
    resource_name_parts = resource_name.split(".")
    resource_name_parts_length = len(resource_name_parts)

    if resource_name_parts_length == 1:
        org = get_resource(Org, resource_name)
        return OrgAuditTarget(org, user_hash)
    elif resource_name_parts_length == 2:
        project = get_resource(Project, resource_name)
        return ProjectAuditTarget(project, user_hash)
    elif resource_name_parts_length == 3:
        item = get_resource(Item, resource_name)
        return ItemAuditTarget(item, user_hash)
    else:
        return InvalidAuditTarget(resource_name, user_hash)

