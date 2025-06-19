#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Clase base abstracta para formularios
"""

from abc import ABC, abstractmethod
from PyQt6.QtWidgets import QDialog

class FormHandler(ABC):
    @abstractmethod
    def create_form(self):
        pass

    @abstractmethod
    def save(self):
        pass