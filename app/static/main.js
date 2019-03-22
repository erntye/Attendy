if (!Array.prototype.includes) {
	Array.prototype.includes = function(searchElement /*, fromIndex*/ ) {
		'use strict';
		if (this === null) {
			throw new TypeError('Array.prototype.includes called on null or undefined');
		}

		var O = Object(this);
		var len = parseInt(O.length, 10) || 0;
		if (len === 0) {
			return false;
		}
		var n = parseInt(arguments[1], 10) || 0;
		var k;
		if (n >= 0) {
			k = n;
		} else {
			k = len + n;
			if (k < 0) {
				k = 0;
			}
		}
		var currentElement;
		while (k < len) {
			currentElement = O[k];
			if (searchElement === currentElement ||
				(searchElement !== searchElement && currentElement !== currentElement)) { // NaN !== NaN
				return true;
			}
			k++;
		}
		return false;
	};
}

var Sudoku = (function() {
	var board;
	var difficulties = {
		easy: .98,
		medium: .5,
		hard: .33
	}

	function Field(input, position) {
		this.position = position;
		this.value = '';
		this.filled = false;
		this.element = input;
		this.tried = [];
		var that = this;
		this.element.addEventListener('change', function(event) {
			if (that.element.value) {
				that.set(that.element.value);
			} else {
				that.clear();
			}
			that.changeCallback(that);
		});
	}
	Field.prototype.set = function(value) {
		this.filled = true;
		this.value = value;
		this.tried.push(value);
	};
	Field.prototype.clear = function() {
		this.value = '';
		this.element.value = '';
		this.filled = false;
		this.setNeutral();
	};
	Field.prototype.reset = function() {
		this.clear();
		this.tried = [];
	};
	Field.prototype.isTried = function(number) {
		return this.tried.includes(number);
	};
	Field.prototype.addNumberToTries = function(number) {
		this.tried.push(number);
	};
	Field.prototype.setNeutral = function () {
		this.element.classList.remove('is--invalid');
		this.element.classList.remove('is--valid');
	};
	Field.prototype.setValid = function() {
		this.element.classList.add('is--valid');
	};
	Field.prototype.setInValid = function() {
		this.element.classList.add('is--invalid');
	};

	function Board(tableSelector) {
		this.blockSize = 3;
		this.hints = false;
		this.fieldSize = this.blockSize * this.blockSize;
		this.element = document.querySelector(tableSelector);
		this.field = [];
		var that = this;
		var changeCallback = function(field) {
			that.onFieldChange(field);
		};
		for (var i = 0; i < this.fieldSize; ++i) {
			var row = [];
			for (var j = 0; j < this.fieldSize; ++j) {
				row[j] = new Field(this.getInputForField(j + 1, i + 1), {
					x: j,
					y: i
				});
				row[j].changeCallback = changeCallback;
			}
			this.field[i] = row;
		}
	}
	Board.prototype.onFieldChange = function(field) {
		var value = field.value;
		field.setNeutral();
		if (this.hints) {
			if (this.checkNumberRow(value, field.position.y, field.position.x)
			   || !field.filled) {
				this.setRowNeutral(field.position.y);
			} else {
				this.setRowInValid(field.position.y);
			}
			if (this.checkNumberColumn(value, field.position.y, field.position.x)
			   || !field.filled) {
				this.setColumnNeutral(field.position.x);
			} else {
				this.setColumnInValid(field.position.x);
			}
		}
		if (this.isFull()) {
			if (this.isCorrect()) {
				this.setValid();
			} else {
				this.setInValid();
			}
		}
	}
	Board.prototype.checkNumber = function(number, row, column) {
		return this.checkNumberBox(number, row, column) &&
			this.checkNumberRow(number, row, column) &&
			this.checkNumberColumn(number, row, column);
	};
	Board.prototype.checkNumberBox = function(number, row, column) {
		var r = Math.abs(Math.round(((row + 1) / this.blockSize) - .55)) * this.blockSize,
			c = Math.abs(Math.round(((column + 1) / this.blockSize) - .55)) * this.blockSize;

		for (var i = r; i < r + this.blockSize; i++) {
			for (var j = c; j < c + this.blockSize; j++) {
				if (this.field[i][j].filled && (i != row && j != column)) {
					if (this.field[i][j].value == number) {
						return false;
					}
				}
			}
		}
		return true;
	};
	Board.prototype.checkNumberRow = function(number, row, column) {
		for (var i = 0; i < this.fieldSize; ++i) {
			if (this.field[row][i].filled && column != i && this.field[row][i].value == number) {
				return false;
			}
		}
		return true;
	};
	Board.prototype.checkNumberColumn = function(number, row, column) {
		for (var i = 0; i < this.fieldSize; i++) {
			if (this.field[i][column].filled && row != i && this.field[i][column].value == number) {
				return false;
			}
		}
		return true;
	};
	Board.prototype.getInputForField = function(x, y) {
		return this.element.querySelector('tr:nth-child(' + y + ') td:nth-child(' + x + ') input');
	};
	Board.prototype.numberHasBeenTried = function(number, row, column) {
		return this.field[row][column].isTried(number);
	};
	Board.prototype.countOfTriedNumbers = function(row, column) {
		return this.field[row][column].tried.length;
	};
	Board.prototype.getRandomNumber = function() {
		return Math.floor(Math.random() * 9) + 1;
	};
	Board.prototype.getNextCell = function(row, column) {
		var r = row,
			c = column;
		if (c < this.fieldSize - 1) {
			c += 1;
		} else {
			c = 0;
			r += 1;
		}
		return {
			row: r,
			column: c
		};
	};
	Board.prototype.setFieldValue = function(value, row, column) {
		this.field[row][column].set(value);
		this.field[row][column].element.value = value;
	};
	Board.prototype.addNumberToFieldTries = function(value, row, column) {
		this.field[row][column].addNumberToTries(value);
	};
	Board.prototype.isFull = function() {
		for (var i = 0; i < this.fieldSize; i++) {
			for (var j = 0; j < this.fieldSize; j++) {
				if (!this.field[i][j].filled) {
					return false;
				}
			}
		}
		return true;
	};
	Board.prototype.isRowFull = function (row) {
		for (var j = 0; j < this.fieldSize; j++) {
				if (!this.field[row][j].filled) {
					return false;
				}
		}
		return true;
	};
	Board.prototype.isCorrect = function() {
		for (var i = 0; i < this.fieldSize; i++) {
			for (var j = 0; j < this.fieldSize; j++) {
				if (this.field[i][j].filled) {
					var value = this.field[i][j].value;
					var correct = this.checkNumber(value, i, j);
					if (!correct) {
						return false;
					}
				}
			}
		}
		return true;
	};
	Board.prototype.setInValid = function() {
		this.element.classList.remove('is--valid');
		this.element.classList.add('is--invalid');
	};
	Board.prototype.setValid = function() {
		this.element.classList.remove('is--invalid');
		this.element.classList.add('is--valid');
	};
	Board.prototype.setRowInValid = function(row) {
		var row = this.field[row][0].element.parentNode.parentNode; 
		row.classList.remove('is--valid');
		row.classList.add('is--invalid');
	};
	Board.prototype.setRowValid = function(row) {
		var row = this.field[row][0].element.parentNode.parentNode; 
		row.classList.remove('is--invalid');
		row.classList.add('is--valid');
	};
	Board.prototype.setRowNeutral = function (row) {
		var row = this.field[row][0].element.parentNode.parentNode; 
		row.classList.remove('is--invalid');
		row.classList.remove('is--valid');
	};
	Board.prototype.setColumnInValid = function(col) {
		for (var row = 0; row < this.fieldSize; row++) {
			this.field[row][col].setInValid()
		}
	};
	Board.prototype.setColumnNeutral = function (col) {
		for (var row = 0; row < this.fieldSize; row++) {
			this.field[row][col].setNeutral()
		}
	};
	Board.prototype.reset = function() {
		this.element.classList.remove('is--valid');
		this.element.classList.remove('is--invalid');
		for (var i = 0; i < this.fieldSize; i++) {
			for (var j = 0; j < this.fieldSize; j++) {
				this.field[i][j].reset();
				this.field[i][j].element.disabled = false;
			}
		}
	}

	function generateFullBoard(board, row, column) {
		if (!board.field[row][column].filled) {
			while (board.countOfTriedNumbers(row, column) < board.fieldSize) {
				var candidate = 0;
				do {
					candidate = board.getRandomNumber();
				} while (board.numberHasBeenTried(candidate, row, column));
				if (board.checkNumber(candidate, row, column)) {
					board.setFieldValue(candidate, row, column);
					var nextCell = board.getNextCell(row, column);
					if (nextCell.row < board.fieldSize &&
						nextCell.column < board.fieldSize) {
						generateFullBoard(board, nextCell.row, nextCell.column);
					}
				} else {
					board.addNumberToFieldTries(candidate, row, column);
				}
			}
			if (!board.isFull()) {
				board.field[row][column].reset();
			}
		}
	}

	function setBoardDifficulty(board, difficulty) {
		for (var i = 0; i < board.fieldSize; i++) {
			for (var j = 0; j < board.fieldSize; j++) {
				if (Math.random() > difficulty) {
					board.field[i][j].reset();
				} else {
					board.field[i][j].element.disabled = true;
				}
			}
		}
	};

	function start() {
		var difficulty = "easy";//document.querySelector('#difficulty').value;
		generateFullBoard(board, 0, 0);
		setBoardDifficulty(board, difficulties[difficulty]);
	};

	function init() {
		board = new Board('#sudoku');
		start();
	};

	return {
		init: init
	};
})();

window.onload = Sudoku.init;