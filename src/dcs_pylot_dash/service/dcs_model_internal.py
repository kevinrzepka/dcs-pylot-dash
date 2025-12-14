# Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
# SPDX-License-Identifier: MIT
# License-Filename: LICENSE
import logging
from dataclasses import dataclass, field
from typing import Self

from dcs_pylot_dash.service.dcs_common_data_types import LoReturnType
from dcs_pylot_dash.service.dcs_model_external import ExternalModel, ExternalModelField
from dcs_pylot_dash.service.units import Unit
from dcs_pylot_dash.utils.string_utils import StringUtils

LOGGER = logging.getLogger(__name__)


class InternalModelError(Exception):
    def __init__(self, msg: str) -> None:
        super().__init__(f"Failed to populate model: {msg}")


@dataclass
class InternalModelField:
    # Local name; may not contain dots
    name: str
    return_type: LoReturnType
    unit: Unit = Unit.NONE
    parent: Self | None = None
    # only set for top-level fields
    lo_function: str | None = None
    # Optional human-readable name
    display_name: str | None = None
    # only set when is_portion
    abs_base_value: float | None = None
    is_portion: bool = False
    fields: dict[str, Self] = field(default_factory=dict)
    list_fields: dict[str, Self] = field(default_factory=dict)
    prototype_ref: Self | None = None
    is_prototype: bool = False
    # If this object is a prototype: Contains all instances
    prototype_implementations: dict[str, Self] = field(default_factory=dict)

    @property
    def is_list_field(self) -> bool:
        return self.return_type == LoReturnType.LIST

    @property
    def has_list_field_in_hierarchy(self) -> bool:
        return self.next_list_field_in_hierarchy is not None

    @property
    def next_list_field_in_hierarchy(self) -> Self | None:
        """
        :return: The first list field going up in the hierarchy (excluding self).
        """
        if self.parent is None:
            return None
        if self.parent.is_list_field:
            return self.parent
        return self.parent.next_list_field_in_hierarchy

    @property
    def dotted_name(self) -> str:
        """
        If this field is a prototype but does not have a function,
        then the dotted name is not the complete name but only a sub-path.
        :return:
        """
        return f"{self.parent.dotted_name}.{self.name}" if self.parent is not None else self.name

    @property
    def effective_display_name(self) -> str:
        return StringUtils.first_non_empty(self.display_name, self.dotted_name)

    @property
    def has_parent(self) -> bool:
        return self.parent is not None

    @property
    def is_root_field(self) -> bool:
        return not self.has_parent

    @property
    def root_field(self) -> Self:
        if self.parent is None:
            return self
        else:
            return self.parent.root_field

    @property
    def has_function(self) -> bool:
        return self.lo_function is not None

    @property
    def is_leaf(self) -> bool:
        return len(self.fields) == 0 and len(self.list_fields) == 0

    def copy_as_instance_from_prototype(self, parent_instance: Self | None = None) -> Self:
        instance: InternalModelField = InternalModelField(
            name=self.name,
            display_name=self.display_name,
            return_type=self.return_type,
            unit=self.unit,
            lo_function=self.lo_function,
            abs_base_value=self.abs_base_value,
            prototype_ref=self,
            parent=parent_instance,
        )
        fields_instances: dict[str, Self] = {
            child_field_name: child_field.copy_as_instance_from_prototype(instance)
            for child_field_name, child_field in self.fields.items()
        }
        list_fields_instances: dict[str, Self] = {
            list_child_field_name: list_child_field.copy_as_instance_from_prototype(instance)
            for list_child_field_name, list_child_field in self.list_fields.items()
        }
        instance.fields |= fields_instances
        instance.list_fields |= list_fields_instances
        self.prototype_implementations[instance.dotted_name] = instance
        return instance


class InternalModel:
    """
    Built from an ExternalModel.
    """

    _prototype_fields: dict[str, InternalModelField]
    _fields: dict[str, InternalModelField]
    _external_model: ExternalModel

    def __init__(self, external_model: ExternalModel) -> None:
        self._prototype_fields = {}
        self._fields = {}
        self._external_model = external_model

    def parse_proto_field(
        self, name: str, ext_proto_field: ExternalModelField, parsed_parent: InternalModelField | None = None
    ) -> InternalModelField:
        """
        Assumption: External prototype fields cannot reference other prototype fields.
        :param name:
        :param ext_proto_field:
        :param parsed_parent:
        :return:
        """
        int_proto_field: InternalModelField = InternalModelField(
            name=name,
            display_name=ext_proto_field.display_name,
            return_type=ext_proto_field.lo_return_type,
            unit=ext_proto_field.unit,
            lo_function=ext_proto_field.lo_function,
            abs_base_value=ext_proto_field.abs_base_value,
            is_prototype=True,
            parent=parsed_parent,
        )

        if not int_proto_field.has_parent:
            self._prototype_fields[name] = int_proto_field

        for child_name, child in ext_proto_field.fields.items():
            child_int_field: InternalModelField = self.parse_proto_field(
                child_name, child, parsed_parent=None if child.references_prototype else int_proto_field
            )

            if child_int_field.is_list_field:
                int_proto_field.list_fields[child_name] = child_int_field
            else:
                int_proto_field.fields[child_name] = child_int_field

        return int_proto_field

    def _add_to_fields_recursively(self, int_field: InternalModelField) -> None:
        self._fields[int_field.dotted_name] = int_field
        for child_field in int_field.fields.values():
            self._add_to_fields_recursively(child_field)
        for child_field in int_field.list_fields.values():
            self._add_to_fields_recursively(child_field)

    def parse_field(
        self, name: str, ext_field: ExternalModelField, parsed_parent: InternalModelField | None = None
    ) -> InternalModelField:
        int_field: InternalModelField
        prototype_field: InternalModelField | None = None
        if ext_field.references_prototype:
            prototype_field: InternalModelField | None = self._prototype_fields.get(ext_field.prototype_ref)
            if prototype_field is None:
                raise InternalModelError(f"prototype {ext_field.prototype_ref} not found")

        if ext_field.is_list_field or not ext_field.references_prototype:
            int_field: InternalModelField = InternalModelField(
                name=name,
                display_name=ext_field.display_name,
                return_type=ext_field.lo_return_type,
                unit=ext_field.unit,
                lo_function=ext_field.lo_function,
                abs_base_value=ext_field.abs_base_value,
                prototype_ref=self._prototype_fields.get(ext_field.prototype_ref),
                is_prototype=False,
                parent=parsed_parent,
            )
        else:
            # must add all children to the fields, if not present
            int_field = prototype_field.copy_as_instance_from_prototype()

        # If it's a list field referencing a prototype, construct an instance of the prototype and assign
        # its fields to this field. The name of the prototype field becomes transparent in this case.
        if ext_field.is_list_field and ext_field.references_prototype:
            proto_instance: InternalModelField = prototype_field.copy_as_instance_from_prototype(int_field)
            int_field.fields = proto_instance.fields
            for f in int_field.fields.values():
                f.parent = int_field
            int_field.list_fields = proto_instance.list_fields
            for f in int_field.list_fields.values():
                f.parent = int_field
        else:
            for child_name, child in ext_field.fields.items():
                child_int_field: InternalModelField = self.parse_field(child_name, child, parsed_parent=int_field)
                if child_int_field.is_list_field:  # should never happen is int_field is a list field itself
                    int_field.list_fields[child_name] = child_int_field
                else:
                    int_field.fields[child_name] = child_int_field

        self._add_to_fields_recursively(int_field)

        return int_field

    def populate(self) -> Self:
        self._fields = {}
        self._prototype_fields = {}

        for name, ext_proto_field in self._external_model.field_prototypes.items():
            self.parse_proto_field(name, ext_proto_field)

        for name, ext_field in self._external_model.fields.items():
            self.parse_field(name, ext_field)

        return self

    def get_field(self, dotted_name: str) -> InternalModelField:
        field: InternalModelField | None = self._fields.get(dotted_name)
        if field is None:
            LOGGER.warning(f"field {dotted_name} not found")
        return field

    @property
    def leaf_fields(self) -> list[InternalModelField]:
        return [f for f in self._fields.values() if f.is_leaf]
