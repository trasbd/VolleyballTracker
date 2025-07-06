document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("addPlayerForm");
  const rosterDiv = document.getElementById("rosterContainer");

  // Load roster on page load
  fetchRoster();

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const name = document.getElementById("playerName").value;
    const jersey = parseInt(document.getElementById("jerseyNumber").value);

    const res = await fetch("/api/players", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, jersey }),
    });

    if (res.ok) {
      form.reset();
      fetchRoster();
    }
  });

  async function fetchRoster() {
    const res = await fetch("/api/players");
    const players = await res.json();
    rosterDiv.innerHTML = "";

    players.forEach(p => {
      const card = document.createElement("div");
      card.className = "player-card";
      card.innerHTML = `#${p.jersey} ${p.name}
        <button onclick="deletePlayer(${p.id})">Delete</button>`;
      rosterDiv.appendChild(card);
    });
  }

  window.deletePlayer = async function (id) {
    await fetch(`/api/players/${id}`, { method: "DELETE" });
    fetchRoster();
  };
});
