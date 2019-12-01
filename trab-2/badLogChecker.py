from pathlib import Path
import os
import sys # Requires Python ver >=3.4!

# Variáveis de entrada e saída
NTHREADS_READ = 0
NTHREADS_WRITE = 0
nReads = 0
nWrites = 0 

#General global variables
reading = 0
writing = 0
waitingToWrite = 0
waitingToRead = 0
writeTurn = 0
sharedVar = -1

readerSignal = 0 
writerSignal = 0

isFirstThread = 1

globalSetterCode = ["global NTHREADS_READ", \
					"global NTHREADS_WRITE", \
					"global nReads", \
					"global nWrites", \
					"global reading", \
					"global writing", \
					"global waitingToWrite", \
					"global waitingToRead", \
					"global writeTurn", \
					"global sharedVar", \
					"global readerSignal", \
					"global writerSignal", \
					"global isFirstThread" ] 

def commandLineParametersRead(nReaderThreads, nWriterThreads, logNReads, logNWrites):
	global NTHREADS_READ
	global NTHREADS_WRITE
	global nReads
	global nWrites
	global reading
	global writing
	global waitingToWrite
	global waitingToRead
	global writeTurn
	global sharedVar
	global readerSignal
	global writerSignal
	global isFirstThread
	global evilDebug

	NTHREADS_READ = nReaderThreads
	NTHREADS_WRITE = nWriterThreads
	nReads = logNReads
	nWrites = logNWrites

	return 1

def tRead(tid, readValue):
	"""Thread tid leu readValue"""
	global NTHREADS_READ
	global NTHREADS_WRITE
	global nReads
	global nWrites
	global reading
	global writing
	global waitingToWrite
	global waitingToRead
	global writeTurn
	global sharedVar
	global readerSignal
	global writerSignal
	global isFirstThread

	if((readValue != sharedVar) or writing > 0): 
		return 0
	else:
		#print('BEFORE DECREMENT READ == ' + str(reading))
		reading -= 1
		#print('AFTER DECREMENT READ == ' + str(reading))
		return 1

def tReaderStartRead(tid):
	"""Thread tid leu readValue"""
	global NTHREADS_READ
	global NTHREADS_WRITE
	global nReads
	global nWrites
	global reading
	global writing
	global waitingToWrite
	global waitingToRead
	global writeTurn
	global sharedVar
	global readerSignal
	global writerSignal
	global isFirstThread

	if(isFirstThread):
		readerSignal = 1
		isFirstThread = 0 #tava no tUnblocked antes

	reading += 1
	writeTurn = -1

	return 1
	
def tReaderBlocked(tid, logWriting, logWaitingToWrite, logWriteTurn):
	"""Leitor foi bloqueado, se writing > 0 || (waitingToWrite > 0 && writeTurn > 0)"""
	global NTHREADS_READ
	global NTHREADS_WRITE
	global nReads
	global nWrites
	global reading
	global writing
	global waitingToWrite
	global waitingToRead
	global writeTurn
	global sharedVar
	global readerSignal
	global writerSignal
	global isFirstThread

	waitingToRead += 1

	if(writing > 0 or (waitingToWrite > 0 and writeTurn > 0)):
		writeTurn = -1 #RISK
		return 1
	else: 
		return 0

def tReaderUnblocked(tid, logWriting, logWaitingToWrite, logWriteTurn):
	"""Leitor foi desbloqueado, pois recebeu signal ou broadcast"""
	global NTHREADS_READ
	global NTHREADS_WRITE
	global nReads
	global nWrites
	global reading
	global writing
	global waitingToWrite
	global waitingToRead
	global writeTurn
	global sharedVar
	global readerSignal
	global writerSignal
	global isFirstThread

	if(readerSignal - 1 < 0): 
		print(readerSignal)
		return 0

	else:
		readerSignal -= 1
		waitingToRead -= 1
		return 1

def tReaderSignalled(tid, logReading):
	"""Leitor enviou signal para Escritores, pois reading == 0"""
	global NTHREADS_READ
	global NTHREADS_WRITE
	global nReads
	global nWrites
	global reading
	global writing
	global waitingToWrite
	global waitingToRead
	global writeTurn
	global sharedVar
	global readerSignal
	global writerSignal
	global isFirstThread

	writerSignal += 1
	writeTurn = 1

	return 1

def tWrote(tid, writtenValue):
	"""Escritor escreveu writtenValue"""
	global NTHREADS_READ
	global NTHREADS_WRITE
	global nReads
	global nWrites
	global reading
	global writing
	global waitingToWrite
	global waitingToRead
	global writeTurn
	global sharedVar
	global readerSignal
	global writerSignal
	global isFirstThread

	if(writtenValue != tid or writing > 1 or reading > 0):
		return 0
	sharedVar = writtenValue
	return 1

def tWriterStartWrite(tid):
	"""Thread tid leu readValue"""
	global NTHREADS_READ
	global NTHREADS_WRITE
	global nReads
	global nWrites
	global reading
	global writing
	global waitingToWrite
	global waitingToRead
	global writeTurn
	global sharedVar
	global readerSignal
	global writerSignal
	global isFirstThread

	if(isFirstThread):
		writerSignal = 1
		isFirstThread = 0

	writing += 1
	return 1


def tWriterBlocked(tid, logReading, logWriting, logWaitingToRead, logWriteTurn):
	"""Escritor foi bloqueado porque reading > 0 || writing > 0 || (waitingToRead > 0 && writeTurn < 0)"""
	global NTHREADS_READ
	global NTHREADS_WRITE
	global nReads
	global nWrites
	global reading
	global writing
	global waitingToWrite
	global waitingToRead
	global writeTurn
	global sharedVar
	global readerSignal
	global writerSignal
	global isFirstThread

	waitingToWrite += 1

	if(reading > 0 or writing > 0 or (waitingToRead > 0 or writeTurn < 0)): #risk
		return 1
	else: 
		return 0

def tWriterUnblocked(tid, logReading, logWriting, logWaitingToRead, logWriteTurn):
	"""Escritor foi desbloqueado pois  ( reading > 0 || writing > 0 || (waitingToRead > 0 && writeTurn < 0) == 0 )""" 
	global NTHREADS_READ
	global NTHREADS_WRITE
	global nReads
	global nWrites
	global reading
	global writing
	global waitingToWrite
	global waitingToRead
	global writeTurn
	global sharedVar
	global readerSignal
	global writerSignal
	global isFirstThread

	if(writerSignal - 1 < 0): 
		return 0

	else:
		writerSignal -= 1
		waitingToWrite -= 1
		return 1

def tWriterSignalledBroadcasted(tid):
	"""Escritor sinalizou para escritores e broadcasteou para leitores"""
	global NTHREADS_READ
	global NTHREADS_WRITE
	global nReads
	global nWrites
	global reading
	global writing
	global waitingToWrite
	global waitingToRead
	global writeTurn
	global sharedVar
	global readerSignal
	global writerSignal
	global isFirstThread

	writerSignal += 1
	readerSignal = NTHREADS_READ
	writing -= 1

	return 1

def main():
	# Lista com arquivos de logs a serem testados
	logFilePaths = []

	# Coloca na lista todos os arquivos log
	for file in os.listdir(Path("logs")):
		if file.endswith(".txt"):
			logFilePaths.append(Path("logs/" + file))

	for currentTestPath in logFilePaths:
		if not currentTestPath.exists():
			print('Error: File does not exist!')
		try:
			# Rotina principal, por arquivo de teste. Checa se todos os comandos foram executados corretamente
			lineCounter = 0
			failedLineCounter = 0
			print('Testando ' + str(currentTestPath)) 
			logFile = open(currentTestPath, 'r')
			for lineNum, command in enumerate(logFile, start=1):
				if(eval(command)):
					pass
					lineCounter += 1
				else:
					print(command.strip("\n") + " falhou na linha " + str(lineNum))
					failedLineCounter += 1
			print('Arquivo testado com sucesso')
			print('Linhas testadas: ' + str(lineCounter + failedLineCounter))
			print('Linhas errôneas detectadas:' + str(failedLineCounter) + '\n')
			logFile.close()

		except OSError as err:
				print("OS error: {0}".format(err))
		except ValueError:
				print("Could not convert data to an integer.")
		except:
				print("Unexpected error:", sys.exc_info()[0])
				raise

if __name__ == '__main__':
	main()