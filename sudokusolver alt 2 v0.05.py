import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class cell(object):
	def __init__(self, value, edit, row, col, block):
		self.originalvalue = value
		self.value = value
		self.edit = edit
		self.loc = {
			"row":row,
			"col":col, 
			"block":block,
		}
		self.AllowedValues = [1, 2, 3, 4, 5, 6, 7, 8, 9]
		self.ExcludedValues = []
		self.pointer = 0
	
class board(cell):
	def __init__(self, matrix = None):
		if matrix != None:
			self.MyMatrix = [[cell(int(matrix[i][j]), int(matrix[i][j])==0, i, j, (i-i%3) + j/3) for j in range(9)] for i in range(9)]
		else:
			self.MyMatrix = [[cell(0, True, i, j, (i-i%3) + j/3) for j in range(9)] for i in range(9)]
		self.AllTypes = ["row", "col", "block"]
		self.TestCycle = 0
		self.HitCount = 0
		self.InitCellType = "row"
		self.InitCellGroup = 0
		self.InitCellHit = 0
		self.EmptyCelCount = 0
		self.StartEmptyCelCount = 0
		for i in range(9):
			for j in range(9):
				if self.MyMatrix[i][j].value == 0:
					self.EmptyCelCount += 1
					self.StartEmptyCelCount += 1
	
	def RequestCell(self, x, y, caller=None):
		try:
			return self.MyMatrix[x][y]
		except:
			print x, y, caller
			raw_input("press enter to close")
	
	def RequestCellValue(self, x, y):
		return self.MyMatrix[x][y].value
	
	def RequestGroupValue(self, Type, Group):
		#todo: reduce number of cells scanned to 9 instead of 81
		ReturnList = []
		for i in range(9):
			for j in range(9):
				if self.RequestCell(i,j).loc[Type] == Group:
					ReturnList.append(self.RequestCell(i,j).value)
		return ReturnList
	
	def RequestGroup(self, Type, Group):
		#todo: reduce number of cells scanned to 9 instead of 81
		ReturnList = []
		for i in range(9):
			for j in range(9):
				if self.RequestCell(i,j).loc[Type] == Group:
					ReturnList.append(self.RequestCell(i,j))
		return ReturnList
	
	def printMatrix(self):
		for i in range(9):
			if i in [3, 6]:
				print '------+-------+-------'
			for j in range(9):
				if j in [3, 6]:
					print '|',
				print self.RequestCell(i,j).value,
			print "" 
	
	def GroupCorrect(self, input_list):
		"""
		checks if all items of check_list are inside input_list
		"""
		check_list = range(1,10) # [1,2,3,4,5,6,7,8,9]
		self.HitCount = 0
		for i in check_list:
			if i in input_list:
				self.HitCount += 1
		return self.HitCount == len(check_list)
	
	def AllCorrect(self):
		logging.debug('---Begin AllCorrect---')
		for Type in self.AllTypes:
			for Group in range(9):
				if not self.GroupCorrect(self.RequestGroupValue(Type, Group)):
					logging.debug('---End AllCorrect---')
					self.InitCellType = Type
					self.InitCellGroup = Group
					self.InitCellHit = self.HitCount
					print self.InitCellType, self.InitCellGroup, self.InitCellHit
					return False
		return True
	
	def UpdateCellValues(self, x, y):
		MyValue = self.RequestCellValue(x,y)
		for k in self.AllTypes:
			for m in self.RequestGroup(k, self.RequestCell(x,y).loc[k]):
				if m.edit and self.RequestCell(x,y) != m and MyValue in m.AllowedValues:
						m.ExcludedValues.append(MyValue)
						m.AllowedValues.remove(MyValue)
	
	def	UpdateAllValues(self):
		for i in range(9): # resets the excluded Values for all cells
			for j in range(9):
				if self.RequestCell(i,j).edit or True:
					self.RequestCell(i,j).AllowedValues = range(1,10)
					self.RequestCell(i,j).ExcludedValues = []
		for i in range(9): # updates a
			for j in range(9):
				if self.RequestCellValue(i,j) != 0:
					self.UpdateCellValues(i,j)
							
							#logging.debug("line 126,"+str(self.TestCycle))
							
							#if 'p' == raw_input("(%s,%s) myvalue=%s, otherv=%s,>" % (i, j, MyValue, m.value,)):
							#	self.printMatrix()
		return True
		
	def checkConsistent(self, input_list):
		self.GroupCorrect(input_list)
		if self.HitCount < 9:
			for i in input_list:
				if i == 0:
					self.HitCount += 1
		return self.HitCount==9	

	def loggingnow(self, position, mylist, matrixprint):
		if self.TestCycle in mylist:	
			logging.debug("TestCycle:"+str(self.TestCycle))
			logging.debug(position)
			if matrixprint:
				self.printMatrix()
			
	def Traceback(self):
		self.TestCycle = 0
		LetMeSee = range(29,40)
		backup = []
		logging.debug('---Begin Traceback---')
		backtrack = False
		self.UpdateAllValues()
		x = 0 
		y = 0
		while x < 9:
			while y < 9 and y >= 0:
				self.TestCycle += 1
				self.loggingnow("Start while Y",LetMeSee,True)
				CursorCell = self.RequestCell(x,y)
				"""if self.TestCycle % 100000 == 0:
					logging.debug("Cycles : "+str(self.TestCycle)+", x:"+str(x)+", y:"+str(y))
				if self.TestCycle % 1000000 == 0:
					self.printMatrix()
					raw_input()
				"""
				if backtrack:
					self.loggingnow("in backtrack"+str(x)+str(y),LetMeSee,False)
					y-=1
					CursorCell = self.RequestCell(x,y)
					if CursorCell.edit:
						CursorCell.value = 0
						if len(CursorCell.AllowedValues) > 1:
							if CursorCell.pointer <= len(CursorCell.AllowedValues)-1:
								self.loggingnow("try next value"+str(x)+str(y),LetMeSee,False)
								CursorCell.pointer += 1
								backtrack = False
								self.UpdateAllValues()
								CursorCell.value = CursorCell.AllowedValues[CursorCell.pointer]
								#remove next logging statement
								logging.debug("exiting backtrack, x:"+str(x)+", y:"+str(y)+", value: "+str(CursorCell.value)+", pointer:"+str(CursorCell.pointer)+", allowed values:"+str(CursorCell.AllowedValues))
								y+=1
							else:
								self.loggingnow("no valid next value",LetMeSee,False)
								logging.debug("In else, x:"+str(x)+", y:"+str(y)+", value: "+str(CursorCell.value)+", pointer:"+str(CursorCell.pointer)+", allowed values:"+str(CursorCell.AllowedValues))
								CursorCell.value = 0
								CursorCell.pointer = 0
								self.UpdateAllValues
						else:
							self.loggingnow("Unexpected: valid values is empty",LetMeSee,False)

				elif CursorCell.edit:
					if CursorCell.value==0:
						if len(CursorCell.AllowedValues) != 0:
							self.loggingnow("Assign value for empty cell",LetMeSee,False)
							CursorCell.pointer = 0
							CursorCell.value = CursorCell.AllowedValues[0]
							self.UpdateCellValues(x,y)
							#remove next logging statement
							logging.debug("Assign value in testcycle: "+str(self.TestCycle)+", x:"+str(x)+", y:"+str(y)+", value:"+str(CursorCell.value)+", allowed values:"+str(CursorCell.AllowedValues))
							y+=1
						elif len(CursorCell.AllowedValues) == 0:
							self.loggingnow("No allowed values for empty cell",LetMeSee,False)
							CursorCell.value = 0
							backtrack = True
							#remove next logging statement
							logging.debug("Start backtrack, cycle: "+str(self.TestCycle)+", x:"+str(x)+", y:"+str(y)+", value:"+str(CursorCell.value)+", allowed values:"+str(CursorCell.AllowedValues))
						else:
							self.loggingnow("Unexpected: else tak",LetMeSee,False)
					else:
						self.loggingnow("Unexpected: else tak2",LetMeSee,False)
				else:
					y+=1
				backup.append(self.MyMatrix)
				if len(backup) > 40:
					if backup[-10] == self.MyMatrix:
						logging.debug(str(self.TestCycle)+' repeating steps, automatic exit')
						return "error"
					backup = backup [1:]
				#End of While Y		
			#remove next logging statement
			logging.debug("Y-range einde bereikt, cycle: "+str(self.TestCycle)+", x:"+str(x)+", y:"+str(y)+", value:"+str(CursorCell.value))
			if backtrack:
				x-=1
				y=8
				if x < 0:
					break
			else:
				x+=1
				y=0
		#End of While X		
		logging.debug('---End Traceback---')
		return 
	
	def RandomSolution():
		return
	
	def TestSudoku(self, mode="Traceback"):
		logging.debug('---start TestSudoku---')
		if self.AllCorrect():
			return True
		logging.info('Intial Sudoku not correct, start solving')
		logging.info("modus: %s testcycle %s, type %s, group %s, hit %s" % (mode, self.TestCycle, self.InitCellType, self.InitCellGroup, self.InitCellHit))
		
		modus = {"Traceback":self.Traceback,"Random":self.RandomSolution,}
		modus[mode]()
		logging.debug('---End TestSudoku---')
		return self.AllCorrect()
	
if __name__ == "__main__":
	sudoku = [[
		"010402050",
		"500000006",
		"000301000",
		"705000408",
		"000000000",
		"208000509",
		"000906000",
		"600000002",
		"070103040",
		],[
		"000050004",
		"000000710",
		"098746300",
		"930002480",
		"085907620",
		"017400035",
		"003621590",
		"029000000",
		"800090000",
		],[
		"123456789",	
		"456789123",
		"789123456",
		"234567891",
		"567891234",
		"891234567",
		"345678912",
		"678912345",
		"912345678",
		],[
		"103056789",
		"056789103",
		"789103056",
		"030567891",
		"567891030",
		"891030567",
		"305678910",
		"678910305",
		"910305678",
		],[
		"000000000",
		"000000000",
		"000000000",
		"000000000",
		"000000000",
		"000000000",
		"000000000",
		"000000000",
		"000000000",
		],[
		"000000000",	
		"456789123",
		"789123456",
		"234567891",
		"567891234",
		"891234567",
		"345678912",
		"678912345",
		"912345678",
		]
	]

	logging.debug('Start')
	a=board(sudoku[len(sudoku)-2])
	a.printMatrix()
	raw_input()
	if a.TestSudoku("Traceback") :
		logging.info('Correct solution found')
	else:
		logging.info('No correct solution found')
	a.printMatrix()
	logging.info('End')
