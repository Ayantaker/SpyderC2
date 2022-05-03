from rich.console import Console
from rich.table import Table

class Style:

	def __init__(self):
		pass


	def create_table(self,title,column,row,table_position):
		table = Table(title=title,style="on grey0")

		for key in column.keys():
			attrs = column[key]
			table.add_column(key,**attrs)

		for entry in row:
			table.add_row(*entry,style='on grey0')

		console = Console()
		console.print(table, justify=table_position)