import React from "react";
import { TableBlock } from "../components/runtime/TableBlock";

const Periodeindisponibilite: React.FC = () => {
  return (
    <div id="page-periodeindisponibilite-4">
    <div id="iw3ja9" style={{"display": "flex", "height": "100vh", "fontFamily": "Arial, sans-serif", "--chart-color-palette": "default"}}>
      <nav id="igzpdj" style={{"width": "250px", "background": "linear-gradient(135deg, #4b3c82 0%, #5a3d91 100%)", "color": "white", "padding": "20px", "overflowY": "auto", "display": "flex", "flexDirection": "column", "--chart-color-palette": "default"}}>
        <h2 id="iwv5r9" style={{"marginTop": "0", "fontSize": "24px", "marginBottom": "30px", "fontWeight": "bold", "--chart-color-palette": "default"}}>{"BESSER"}</h2>
        <div id="imptjc" style={{"display": "flex", "flexDirection": "column", "flex": "1", "--chart-color-palette": "default"}}>
          <a id="imr0al" style={{"color": "white", "textDecoration": "none", "padding": "10px 15px", "display": "block", "background": "transparent", "borderRadius": "4px", "marginBottom": "5px", "--chart-color-palette": "default"}} href="/centrecongres">{"CentreCongres"}</a>
          <a id="i17oqz" style={{"color": "white", "textDecoration": "none", "padding": "10px 15px", "display": "block", "background": "transparent", "borderRadius": "4px", "marginBottom": "5px", "--chart-color-palette": "default"}} href="/gestionnaire">{"Gestionnaire"}</a>
          <a id="i7y6ik" style={{"color": "white", "textDecoration": "none", "padding": "10px 15px", "display": "block", "background": "transparent", "borderRadius": "4px", "marginBottom": "5px", "--chart-color-palette": "default"}} href="/elementcentre">{"ElementCentre"}</a>
          <a id="ift7ce" style={{"color": "white", "textDecoration": "none", "padding": "10px 15px", "display": "block", "background": "transparent", "borderRadius": "4px", "marginBottom": "5px", "--chart-color-palette": "default"}} href="/reservation">{"Reservation"}</a>
          <a id="izd4tv" style={{"color": "white", "textDecoration": "none", "padding": "10px 15px", "display": "block", "background": "rgba(255,255,255,0.2)", "borderRadius": "4px", "marginBottom": "5px", "--chart-color-palette": "default"}} href="/periodeindisponibilite">{"PeriodeIndisponibilite"}</a>
          <a id="intn1e" style={{"color": "white", "textDecoration": "none", "padding": "10px 15px", "display": "block", "background": "transparent", "borderRadius": "4px", "marginBottom": "5px", "--chart-color-palette": "default"}} href="/evenement">{"Evenement"}</a>
          <a id="inn3ds" style={{"color": "white", "textDecoration": "none", "padding": "10px 15px", "display": "block", "background": "transparent", "borderRadius": "4px", "marginBottom": "5px", "--chart-color-palette": "default"}} href="/salle">{"Salle"}</a>
          <a id="is0olu" style={{"color": "white", "textDecoration": "none", "padding": "10px 15px", "display": "block", "background": "transparent", "borderRadius": "4px", "marginBottom": "5px", "--chart-color-palette": "default"}} href="/materiel">{"Materiel"}</a>
          <a id="ir0nqt" style={{"color": "white", "textDecoration": "none", "padding": "10px 15px", "display": "block", "background": "transparent", "borderRadius": "4px", "marginBottom": "5px", "--chart-color-palette": "default"}} href="/prestation">{"Prestation"}</a>
        </div>
        <p id="innljk" style={{"marginTop": "auto", "paddingTop": "20px", "borderTop": "1px solid rgba(255,255,255,0.2)", "fontSize": "11px", "opacity": "0.8", "textAlign": "center", "--chart-color-palette": "default"}}>{"© 2026 BESSER. All rights reserved."}</p>
      </nav>
      <main id="i712mg" style={{"flex": "1", "padding": "40px", "overflowY": "auto", "background": "#f5f5f5", "--chart-color-palette": "default"}}>
        <h1 id="ijf231" style={{"marginTop": "0", "color": "#333", "fontSize": "32px", "marginBottom": "10px", "--chart-color-palette": "default"}}>{"PeriodeIndisponibilite"}</h1>
        <p id="i6yhol" style={{"color": "#666", "marginBottom": "30px", "--chart-color-palette": "default"}}>{"Manage PeriodeIndisponibilite data"}</p>
        <TableBlock id="table-periodeindisponibilite-4" styles={{"width": "100%", "minHeight": "400px", "--chart-color-palette": "default"}} title="PeriodeIndisponibilite List" options={{"showHeader": true, "stripedRows": false, "showPagination": true, "rowsPerPage": 5, "actionButtons": true, "columns": [{"label": "DateDebut", "column_type": "field", "field": "dateDebut", "type": "date", "required": true}, {"label": "DateFin", "column_type": "field", "field": "dateFin", "type": "date", "required": true}, {"label": "Motif", "column_type": "field", "field": "motif", "type": "str", "required": true}], "formColumns": [{"column_type": "field", "field": "dateDebut", "label": "dateDebut", "type": "date", "required": true, "defaultValue": null}, {"column_type": "field", "field": "dateFin", "label": "dateFin", "type": "date", "required": true, "defaultValue": null}, {"column_type": "field", "field": "motif", "label": "motif", "type": "str", "required": true, "defaultValue": null}, {"column_type": "lookup", "path": "elementcentre_2", "field": "elementcentre_2", "lookup_field": "nom", "entity": "ElementCentre", "type": "str", "required": true}]}} dataBinding={{"entity": "PeriodeIndisponibilite", "endpoint": "/periodeindisponibilite/"}} />
      </main>
    </div>    </div>
  );
};

export default Periodeindisponibilite;
