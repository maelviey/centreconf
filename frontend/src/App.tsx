import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import { TableProvider } from "./contexts/TableContext";
import Centrecongres from "./pages/Centrecongres";
import Gestionnaire from "./pages/Gestionnaire";
import Elementcentre from "./pages/Elementcentre";
import Reservation from "./pages/Reservation";
import Periodeindisponibilite from "./pages/Periodeindisponibilite";
import Evenement from "./pages/Evenement";
import Salle from "./pages/Salle";
import Materiel from "./pages/Materiel";
import Prestation from "./pages/Prestation";

function App() {
  return (
    <TableProvider>
      <div className="app-container">
        <main className="app-main">
          <Routes>
            <Route path="/centrecongres" element={<Centrecongres />} />
            <Route path="/gestionnaire" element={<Gestionnaire />} />
            <Route path="/elementcentre" element={<Elementcentre />} />
            <Route path="/reservation" element={<Reservation />} />
            <Route path="/periodeindisponibilite" element={<Periodeindisponibilite />} />
            <Route path="/evenement" element={<Evenement />} />
            <Route path="/salle" element={<Salle />} />
            <Route path="/materiel" element={<Materiel />} />
            <Route path="/prestation" element={<Prestation />} />
            <Route path="/" element={<Navigate to="/centrecongres" replace />} />
            <Route path="*" element={<Navigate to="/centrecongres" replace />} />
          </Routes>
        </main>
      </div>
    </TableProvider>
  );
}
export default App;
