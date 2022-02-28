from rich.console import Console
from rich.table import Table

class Style:

	def __init__(self):
		pass


	def create_table(self,title,column,row,table_position):
		table = Table(title=title,style="magenta")

		for key in column.keys():
			attrs = column[key]
			table.add_column(key,**attrs)

		for entry in row:
			table.add_row(*entry)

		console = Console()
		console.print(table, justify=table_position)