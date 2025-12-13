let selectedSeries = JSON.parse(localStorage.getItem("selectedSeries")) || [];

function fetchSeriesList() {
  document.getElementById("load-series-button").style.display = "none";
  document.getElementById("loading").style.display = "block";

  fetch("/get_series_list", {
    method: "POST",
  })
    .then((res) => res.json())
    .then((seriesNames) => {
      const listContainer = document.getElementById("series-list");
      listContainer.innerHTML = "";

      seriesNames.sort((a, b) => {
        const licenceCompare = a.licence_group.localeCompare(
          b.licence_group,
          "en",
          { sensitivity: "base" }
        );
        if (licenceCompare !== 0) return licenceCompare;
        const categoryCompare = a.category.localeCompare(b.category, "en", {
          sensitivity: "base",
        });
        if (categoryCompare !== 0) return categoryCompare;
        return a.serie_name.localeCompare(b.serie_name, "en", {
          sensitivity: "base",
        });
      });

      seriesNames.forEach((serie) => {
        const isChecked = selectedSeries.includes(serie.serie_name);
        const div = document.createElement("div");
        div.innerHTML = `
                            <label>
                                <input type="checkbox" value="${
                                  serie.serie_name
                                }" ${
          isChecked ? "checked" : ""
        } onchange="toggleSeries(this)">
                                Licencia: ${serie.licence_group} - Categoria: ${
          serie.category
        } - ${serie.serie_name}
                            </label>
                        `;
        listContainer.appendChild(div);
      });

      document
        .getElementById("search-box")
        .addEventListener("input", function () {
          const filter = this.value.toLowerCase();
          const labels = listContainer.querySelectorAll("label");
          labels.forEach((label) => {
            label.parentElement.style.display = label.textContent
              .toLowerCase()
              .includes(filter)
              ? ""
              : "none";
          });
        });
    })
    .finally(() => {
      document.getElementById("loading").style.display = "none";
      document.getElementById("loadTableButton").style.display = "block";
      document.getElementById("search-box").style.display = "block"
    });
}

function toggleSeries(checkbox) {
  const value = checkbox.value;
  if (checkbox.checked) {
    if (!selectedSeries.includes(value)) selectedSeries.push(value);
  } else {
    selectedSeries = selectedSeries.filter((s) => s !== value);
  }
  localStorage.setItem("selectedSeries", JSON.stringify(selectedSeries));
}

function sortTable(table, col) {
  const tbody = table.tBodies[0];
  const rows = Array.from(tbody.querySelectorAll("tr"));

  const asc = !(
    table.dataset.sortAsc === "true" && table.dataset.sortCol == col
  );
  table.dataset.sortAsc = asc;
  table.dataset.sortCol = col;

  rows.sort((a, b) => {
    let A = a.children[col].innerText.trim();
    let B = b.children[col].innerText.trim();
    const numA = parseFloat(A.replace(",", "."));
    const numB = parseFloat(B.replace(",", "."));
    const isNumeric = !isNaN(numA) && !isNaN(numB);

    if (isNumeric) {
      return asc ? numA - numB : numB - numA;
    } else {
      return asc
        ? A.localeCompare(B, undefined, {
            sensitivity: "base",
            numeric: true,
          })
        : B.localeCompare(A, undefined, {
            sensitivity: "base",
            numeric: true,
          });
    }
  });

  rows.forEach((row) => tbody.appendChild(row));
}

function makeTableSortable() {
  const table = document.querySelector("#table-container table");
  if (!table) return;
  table.querySelectorAll("th").forEach((th, i) => {
    th.style.cursor = "pointer";
    th.addEventListener("click", () => sortTable(table, i));
  });
}

function loadTable() {
  document.getElementById("loading").style.display = "block";

  fetch("/get_series_table", {
    method: "POST",
  })
    .then((response) => response.json())
    .then((data) => {
      let filteredSeries = data.series.filter((s) =>
        selectedSeries.includes(s.serie_name)
      );

      let table = "<table><thead><tr>";
      table +=
        "<th>Serie</th><th>Licencia</th><th>Race Week</th><th>Category</th><th>Cars</th>";

      const futureDates = data.all_dates;

      futureDates.forEach((date) => {
        table += `<th>${date}</th>`;
      });

      table += "</tr></thead><tbody>";

      filteredSeries.forEach((serie) => {
        let carsByClass = {};
        serie.cars_ids.forEach((car) => {
          if (!carsByClass[car.car_class]) carsByClass[car.car_class] = [];
          carsByClass[car.car_class].push(car);
        });

        let carsHTML = "";
        for (const [carClass, cars] of Object.entries(carsByClass)) {
          carsHTML += `<div style="margin-bottom:4px;"><strong>${carClass}</strong>: `;
          cars.forEach((car, idx) => {
            const style =
              car.car_owned === "true"
                ? "font-weight:bold; background:#00ff2f; padding:2px 4px; border-radius:4px;"
                : "";
            carsHTML += `<span style="${style}">${car.car_name}</span>${
              idx < cars.length - 1 ? ", " : ""
            }`;
          });
          carsHTML += "</div>";
        }

        table += `<tr>
                            <td style="border: 1px solid black">${serie.serie_name}</td>
                            <td style="border: 1px solid black">${serie.licence_group}</td>
                            <td style="border: 1px solid black">${serie.race_week}</td>
                            <td style="border: 1px solid black">${serie.category}</td>
                            <td style="border: 1px solid black; text-align:left;">${carsHTML}</td>`;

        futureDates.forEach((date) => {
          let track = "-";
          let color = "transparent";
          let trackOwned = "false";
          serie.schedules.forEach((sch) => {
            if (sch.start_date_week === date) {
              track = sch.track_id;
              color = sch.track_id_color || "transparent";
              trackOwned = sch.track_owned || "false";
            }
          });
          table += `<td style="background-color:${color};`;
          if (trackOwned === "true") {
            table += `border-style:solid"> <span style="background-color:#00ff2f;">${track}</span> </td>`;
          } else {
            table += `border-style:dotted">${track}</td>`;
          }
        });

        table += "</tr>";
      });

      table += "</tbody></table>";
      document.getElementById("table-container").innerHTML = table;
      makeTableSortable();
    })
    .finally(() => {
      document.getElementById("loading").style.display = "none";
    });
}
