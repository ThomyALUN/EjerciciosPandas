import pandas as pd

# Función que genera nuevos indices numericos, desde 0 hasta n-1.
# n: Númmero total de filas del DataFrame
def nuevosIndices(tabla):
    tabla.index=[i for i in range(len(tabla))]
    return tabla

def depurarColumnaIndices(tabla):
    nombrePrimeraCol=tabla.columns[0]
    primeraColumna=tabla[nombrePrimeraCol]
    indices=tabla.index
    if all([indices[i]==primeraColumna[i] for i in indices]):
        tabla=tabla.drop([nombrePrimeraCol],axis=1)
    return tabla

# Función que elimina filas, teniendo en cuenta una columna de valores numéricos.
# Se busca depurar las filas que contengan datos atípicos.
def depurarNumeros(tabla, nombreCol, limInf, limSup):
    indices=tabla.index
    for i in indices:
        fila=tabla.loc[i]
        if fila[nombreCol]<limInf or fila[nombreCol]>limSup:
            tabla=tabla.drop([i],axis=0)
    tabla=nuevosIndices(tabla)
    return tabla

# Función que elimina columnas que tengan un porcentaje de valores indefinidos (NaN) demasiado grande para el problema a tratar.
def depurarColumnas(tabla, porcentaje):
    size=len(tabla)
    columnas=tabla.columns
    for columna in columnas:
        booleanos=tabla[columna].notnull()
        if sum(booleanos)<size*porcentaje:
            tabla=tabla.drop([columna],axis=1)
    tabla=nuevosIndices(tabla)
    return tabla

# Función que da información detallada de cada columna del DataFrame.
# Usar con DataFrames grandes.
def describirColumnas(tabla, factor):
    size=len(tabla)
    columnas=tabla.columns
    for i in range(len(columnas)//factor+1):
        subgrupo=columnas[0+i*factor:factor+i*factor]
        print('*'*85+'SUBGRUPO #'+str(i+1)+'*'*85+'\n')
        print(datos[subgrupo].describe(include='all'))
        input('\nPresione la tecla Enter para mostrar el siguiente subgrupo.\n')

def mostrarColumnasNumericas(tabla):
    pass

datos=pd.read_csv('fifa.csv')
datos=depurarColumnaIndices(datos)
datos=depurarColumnas(datos, 0.30)
datos=depurarNumeros(datos, 'Age', 10, 100) #Se limita la edad en un rango entre 10 y 100 años
describirColumnas(datos, 8)

datos.to_csv('nuevoFifa.csv')