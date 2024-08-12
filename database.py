import sqlite3

class Data_base:
    
    def __init__(self, name = 'system.db') -> None:
        self.name = name

    def connect(self):
        self.connection = sqlite3.connect(self.name)

    def close_connection(self):
        try:
            self.connection.close()
        except:
            pass
    
    def create_table_company(self):

        cursor = self.connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Empresas(
            
            CNPJ TEXT,
            NOME TEXT,
            LOGADOURO TEXT,              
            NUMERO TEXT,               
            COMPLEMENTO TEXT,
            BAIRRO TEXT,
            MUNICIPIO TEXT,
            UF TEXT,
            CEP TEXT,               
            TELEFONE TEXT,
            EMAIL TEXT,
            
            PRIMARY KEY(CNPJ)
            );
                                    
        



        """)

    def register_company(self, fullDataSet):

        campos_tabela = ('CNPJ', 'NOME', 'LOGADOURO', 'NUMERO', 'COMPLEMENTO', 
        'BAIRRO', 'MUNICIPIO', 'UF', 'CEP', 'TELEFONE', 'EMAIL')

        qntd = ("?,?,?,?,?,?,?,?,?,?,?")
        cursor = self.connection.cursor()

        try:
            cursor.execute(f"""INSERT INTO Empresas {campos_tabela}
            values({qntd})""", fullDataSet)
            self.connection.commit()
            return("OK")
        
        except:
            return "Erro"
        
    def select_all_companies(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM Empresas ORDER BY NOME")
            empresas = cursor.fetchall()
            return empresas
        except:
            pass

    def delete_company(self, id):
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"DELETE FROM Empresas WHERE CNPJ = '{id}' ")
            
            self.connection.commit()

            return "Cadastro excluido com sucesso!"
        except:
            return "Erro ao excluir cadastro!"
        
    def update_company(self, fullDataSet):
        cursor = self.connection.cursor()
        cursor.execute(f""" UPDATE Empresas set
            
            CNPJ = '{fullDataSet[0]}',
            NOME = '{fullDataSet[1]}',
            LOGADOURO = '{fullDataSet[2]}',              
            NUMERO = '{fullDataSet[3]}',               
            COMPLEMENTO = '{fullDataSet[4]}',
            BAIRRO = '{fullDataSet[5]}',
            MUNICIPIO = '{fullDataSet[6]}',
            UF = '{fullDataSet[7]}',
            CEP = '{fullDataSet[8]}',              
            TELEFONE = '{fullDataSet[9]}',
            EMAIL = '{fullDataSet[10]}'

            WHERE CNPJ = '{fullDataSet[0]}'""")
        
        self.connection.commit()

    