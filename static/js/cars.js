function fetchCarsList() {
  document.getElementById("loading").style.display = "block";
  document.getElementById("load-cars-button").style.display = "none";

  fetch("/get_all_cars", {
    method: "POST",
  })
    .then((res) => res.json())
    .then((carsData) => {
      let table = "<table><thead><tr>";
      table +=
        "<th>Imagen</th><th>Marca</th><th>Modelo</th><th>Nombre</th><th>HP</th><th>Peso</th><th>Tiene Luces</th><th>No retirado (Legacy)</th><th>Precio</th><th>Link</th>";
      table += "</tr></thead><tbody>";

      Object.values(carsData.cars).forEach((car) => {
        const imgUrl = `https://images-static.iracing.com/${car.folder}/${car.small_image}`;
        table += `
              <tr>
                <td><img src="${imgUrl}" alt="${
          car.car_name
        }" class="car-thumb"></td>
                <td>${car.car_make ?? "-"}</td>
                <td>${car.car_model ?? "-"}</td>
                <td>${car.car_name ?? "-"}</td>
                <td>${car.hp ?? "-"} HP</td>
                <td>${car.car_weight ?? "-"} Kg</td>
                <td>${car.has_headlights ? "✔️" : "❌"}</td>
                <td>${car.retired ? "❌" : "✔️"}</td>
                <td>${car.price_display ?? "-"}</td>
                <td><a href="${
                  car.site_url ?? ""
                }" target="_blank" class="car-link">${
          car.site_url ?? "-"
        }</a></td>
              </tr>`;
      });

      table += "</tbody></table>";
      document.getElementById("cars-container").innerHTML = table;
      document.getElementById("search-box").style.display = "block";

      // filtro en vivo
      document
        .getElementById("search-box")
        .addEventListener("input", function () {
          const filter = this.value.toLowerCase();
          document
            .querySelectorAll("#cars-container tbody tr")
            .forEach((row) => {
              const text = row.innerText.toLowerCase();
              row.style.display = text.includes(filter) ? "" : "none";
            });
        });
    })
    .finally(() => {
      document.getElementById("loading").style.display = "none";
      document.getElementById("load-cars-button").style.display = "block";
      document.getElementById("cars-container").style.display = "block";
      
    });
}
