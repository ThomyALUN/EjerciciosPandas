import pandas as pd

datos=pd.read_csv('titanic_train.csv')
cabecera=['ID','Clase','Nombre','Sexo','Edad','Hermanos','Hijos','Ticket','Tarifa','Cabina','Embarque','Bote','Cuerpo','Hogar/Destino','Sobrevivió']
datos.columns=cabecera
print(datos.dtypes)
print(datos.describe(include='all'))
print(datos.info)

datos.to_csv('titanic.csv')