class Filtering {
    constructor (tableID, inputID, indexes) {
        this.table = document.getElementById(tableID);
        this.input = document.getElementById(inputID);
        this.tr = [...this.table.getElementsByTagName("tr")];
        this.indexes = indexes;
    }

    searchForOccurrence (index) {
        let keyword = this.input.value.toUpperCase();
        for (let tr of this.tr) {
            let td = tr.getElementsByTagName('td')[index];
            if (td) {
                tr.style.display =
                    (td.innerHTML.toUpperCase().indexOf(keyword) > -1) ? "" : "none";
            }
        }
    }

    filterNumerical (index) {
        const re = new RegExp("^(\s*\[0-9]{1,})");
        const operator = document.getElementById("operator").value;
        let input = this.input.value.match(re)[0];
        input = parseInt(input);
        for (let tr of this.tr) {
            let td = tr.getElementsByTagName('td')[index];
            if (td) {
                td = parseInt(td.innerHTML);
                tr.style.display = (this.checkCondition(operator, td, input)) ? "" : "none";
            }
        }
    }
    checkCondition(operator, td, input) {
        switch (operator) {
            case "=":
                return (td === input);
            case ">":
                return (td > input);
            case ">=":
                return (td >= input);
            case "<":
                return (td < input);
            case "<=":
                return (td <= input);
        }
    }
}

