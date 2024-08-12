# Importando as bibliotecas necessárias ----------------------
from PySide6 import QtCore
from PySide6.QtCore import QCoreApplication
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (QApplication, QTableWidgetItem, QMainWindow, QMessageBox)
from ui_main import Ui_MainWindow
import sys
from ui_functions import consulta_cnpj
from database import Data_base
import pandas as pd
import sqlite3

# Criando a classe MainWindow --------------------------------
class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("PyCadaster - Sistema de Cadastro de Empresas")
        appIcon = QIcon(U"logo.png")
        self.setWindowIcon(appIcon)


    # Função abrir menu ---------------------------------------

        # Botão Menu --------------------------------------------------------
        self.toggle_btn.clicked.connect(self.leftMenu)
        ######################################################################
        
        # Páginas do sitema ------------------------------------------------
        self.btn_home.clicked.connect(lambda: self.Pages.setCurrentWidget(self.pg_home))
        self.btn_cadastrar.clicked.connect(lambda: self.Pages.setCurrentWidget(self.pg_cadastrar))
        self.btn_contatos.clicked.connect(lambda: self.Pages.setCurrentWidget(self.pg_contatos))
        self.btn_sobre.clicked.connect(lambda: self.Pages.setCurrentWidget(self.pg_sobre))
        ##########################################################################################

        ######################################################################################
        # Preencher automaticamente os dados do cnpj
        self.txt_cnpj.editingFinished.connect(self.consult_api)
        #######################################################################################

        # Cadastrar os usuários --------------------------------
        self.btn_cadastro_usuarios.clicked.connect(self.cadastrar_empresas)

        # Atualizar e alterar dados --------------------------------
        self.btn_alterar.clicked.connect(self.updata_company)
        # Excluir dados dos usuários --------------------------------
        self.btn_excluir.clicked.connect(self.deletar_empresa)
        # Gerar tabela Excel ----------------------------------------
        self.btn_exel.clicked.connect(self.gerar_excel)
        self.btn_exel.clicked.connect(self.gerar_excel2)

        self.buscar_empresas()

    def leftMenu(self):
        width = self.left_menu.width()

        if width == 9:
            newWidth = 200
        else:
            newWidth = 9

        self.animation = QtCore.QPropertyAnimation(self.left_menu, b"maximumWidth")
        self.animation.setDuration(500)
        self.animation.setStartValue(width)
        self.animation.setEndValue(newWidth)
        self.animation.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
        self.animation.start()

    def consult_api(self):
        campos = consulta_cnpj(self.txt_cnpj.text())

        self.txt_nome.setText(campos[0])
        self.txt_logadouro.setText(campos[1])
        self.txt_numero.setText(campos[2])
        self.txt_complemento.setText(campos[3])
        self.txt_bairro.setText(campos[4])
        self.txt_municipio.setText(campos[5])
        self.txt_uf.setText(campos[6])
        self.txt_cep.setText(campos[7].replace('.', '').replace('-', ''))
        self.txt_telefone.setText(campos[8].replace('(', '').replace('-', '').replace(')', ''))
        self.txt_email.setText(campos[9])

    def cadastrar_empresas(self):
        db = Data_base()
        db.connect()

        fullDataSet = (

            self.txt_cnpj.text(), self.txt_nome.text(), self.txt_logadouro.text(), self.txt_numero.text(), 
            self.txt_complemento.text(), self.txt_bairro.text(), self.txt_municipio.text(), self.txt_uf.text(), 
            self.txt_cep.text(), self.txt_telefone.text(), self.txt_email.text() 
        )

        # Cadastrar no banco de dados --------------------------------------
        resp = db.register_company(fullDataSet)

        if resp == "OK":
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Cadastro Realizado")
            msg.setText("Cadastro Realizado com Sucesso")
            msg.exec()
            db.close_connection()
            return
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Erro")
            msg.setText("Erro ao cadastrar, verigique se as informações foram preenchidas corretamente")
            msg.exec()
            db.close_connection()
            return

    def buscar_empresas(self):

        db = Data_base()
        db.connect()
        result = db.select_all_companies()

        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(len(result))

        for row, text in enumerate(result):
            for column, data in enumerate(text):
                self.tableWidget.setItem(row, column, QTableWidgetItem(str(data)))

        db.close_connection()

    def updata_company(self):

        dados = []
        update_dados = []

        for row in range(self.tableWidget.rowCount()):
            for column in range(self.tableWidget.columnCount()):
                dados.append(self.tableWidget.item(row, column).text())
            update_dados.append(dados)
            dados = []

        # Atualizar dados no banco
        db = Data_base()
        db.connect() 

        for emp in update_dados:
            db.update_company(tuple(emp))

        db.close_connection()

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Atualização de Dados")
        msg.setText("Dados atualizados com sucesso!")
        msg.exec()

        self.tableWidget.reset()
        self.buscar_empresas()

    def deletar_empresa(self):

        db = Data_base()
        db.connect()

        msg = QMessageBox()
        msg.setWindowTitle("Excluir")
        msg.setText("Este registor será excluído.")
        msg.setInformativeText("Você tem certeza que deseja excluir?")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        resp = msg.exec()

        if resp == QMessageBox.Yes:
            cnpj = self.tableWidget.selectionModel().currentIndex().siblingAtColumn(0).data()
            result = db.delete_company(cnpj)
            self.buscar_empresas()

            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("EMPRESAS")
            msg.setText(result)
            msg.exec()

        db.close_connection()

    def gerar_excel(self):

        dados = []
        all_dados = []

        for row in range(self.tableWidget.rowCount()):
            for column in range(self.tableWidget.columnCount()):
                dados.append(self.tableWidget.item(row, column).text())

            all_dados.append(dados)
            dados = []

        columns = ['CNPJ', 'NOME', 'LOGADOURO', 'NUMERO', 'COMPLEMENTO', 'BAIRRO', 'MUNICIPIO', 
                'UF', 'CEP', 'TELEFONE', 'EMAIL']
        
        empresas = pd.DataFrame(all_dados, columns=columns)
        empresas.to_excel("Empresas.xlsx",sheet_name='empresas', index=False)

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Excel")
        msg.setText("Relatório Excel gerado com Sucesso!")
        msg.exec()

    def gerar_excel2(self):

        cnx = sqlite3.connect("system.db")

        empresas = pd.read_sql_query("""SELECT * FROM Empresas""", cnx)

        empresas.to_excel("Empresas.xlsx",sheet_name='empresas', index=False)

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Excel")
        msg.setText("Relatório Excel gerado com Sucesso!")
        msg.exec()



if __name__ == "__main__":

    db = Data_base()
    db.connect()
    db.create_table_company()
    db.close_connection()

    app =QApplication(sys.argv)
    Window = MainWindow()
    Window.show()
    app.exec()

