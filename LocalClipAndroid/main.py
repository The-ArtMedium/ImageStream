# main.py
import os, subprocess, threading
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from kivy.utils import platform

# Global Translation Dictionary
LOCALES = {
    'en': {'select': "SELECT MASTER FOOTAGE", 'load': "LOAD MOVIE", 'in': "SET IN", 'out': "SET OUT", 'save': "SAVE LOSSLESS CLIP", 'ready': "Ready", 'saving': "Saving...", 'close': "CLOSE MASTER", 'exit': "EXIT APP"},
    'es': {'select': "SELECCIONAR MAESTRO", 'load': "CARGAR PELÍCULA", 'in': "MARCAR INICIO", 'out': "MARCAR FINAL", 'save': "GUARDAR SIN PÉRDIDA", 'ready': "Listo", 'saving': "Guardando...", 'close': "CERRAR MAESTRO", 'exit': "SALIR"},
    'fr': {'select': "SÉLECTIONNER LE MASTER", 'load': "CHARGER LE FILM", 'in': "DÉBUT", 'out': "FIN", 'save': "ENREGISTRER SANS PERTE", 'ready': "Prêt", 'saving': "Enregistrement...", 'close': "FERMER LE MASTER", 'exit': "QUITTER"},
    'pt': {'select': "SELECIONAR MASTER", 'load': "CARREGAR FILME", 'i