import React from "react";
import { TableBlock } from "../components/runtime/TableBlock";

const Evenement: React.FC = () => {
  return (
    <div id="page-evenement-5">
    <div id="ilc0sj" style={{"display": "flex", "height": "100vh", "fontFamily": "Arial, sans-serif", "--chart-color-palette": "default"}}>
      <nav id="iyuhd7" style={{"width": "250px", "background": "linear-gradient(135deg, #4b3c82 0%, #5a3d91 100%)", "color": "white", "padding": "20px", "overflowY": "auto", "display": "flex", "flexDirection": "column", "--chart-color-palette": "default"}}>
        <h2 id="ih9t3a" style={{"marginTop": "0", "fontSize": "24px", "marginBottom": "30px", "fontWeight": "bold", "--chart-color-palette": "default"}}>{"BESSER"}</h2>
        <div id="i457dq" style={{"display": "flex", "flexDirection": "column", "flex": "1", "--chart-color-palette": "default"}}>
          <a id="iqx6bc" style={{"color": "white", "textDecoration": "none", "padding": "10px 15px", "display": "block", "background": "transparent", "borderRadius": "4px", "marginBottom": "5px", "--chart-color-palette": "default"}} href="/centrecongres">{"CentreCongres"}</a>
          <a id="ii3dxg" style={{"color": "white", "textDecoration": "none", "padding": "10px 15px", "display": "block", "background": "transparent", "borderRadius": "4px", "marginBottom": "5px", "--chart-color-palette": "default"}} href="/gestionnaire">{"Gestionnaire"}</a>
          <a id="ivixtg" style={{"color": "white", "textDecoration": "none", "padding": "10px 15px", "display": "block", "background": "transparent", "borderRadius": "4px", "marginBottom": "5px", "--chart-color-palette": "default"}} href="/elementcentre">{"ElementCentre"}</a>
          <a id="i57eer" style={{"color": "white", "textDecoration": "none", "padding": "10px 15px", "display": "block", "background": "transparent", "borderRadius": "4px", "marginBottom": "5px", "--chart-color-palette": "default"}} href="/reservation">{"Reservation"}</a>
          <a id="i026q3" style={{"color": "white", "textDecoration": "none", "padding": "10px 15px", "display": "block", "background": "transparent", "borderRadius": "4px", "marginBottom": "5px", "--chart-color-palette": "default"}} href="/periodeindisponibilite">{"PeriodeIndisponibilite"}</a>
          <a id="iebuil" style={{"color": "white", "textDecoration": "none", "padding": "10px 15px", "display": "block", "background": "rgba(255,255,255,0.2)", "borderRadius": "4px", "marginBottom": "5px", "--chart-color-palette": "default"}} href="/evenement">{"Evenement"}</a>
          <a id="injqbi" style={{"color": "white", "textDecoration": "none", "padding": "10px 15px", "display": "block", "background": "transparent", "borderRadius": "4px", "marginBottom": "5px", "--chart-color-palette": "default"}} href="/salle">{"Salle"}</a>
          <a id="igfed9" style={{"color": "white", "textDecoration": "none", "padding": "10px 15px", "display": "block", "background": "transparent", "borderRadius": "4px", "marginBottom": "5px", "--chart-color-palette": "default"}} href="/materiel">{"Materiel"}</a>
          <a id="id5g0s" style={{"color": "white", "textDecoration": "none", "padding": "10px 15px", "display": "block", "background": "transparent", "borderRadius": "4px", "marginBottom": "5px", "--chart-color-palette": "default"}} href="/prestation">{"Prestation"}</a>
        </div>
        <p id="icae9r" style={{"marginTop": "auto", "paddingTop": "20px", "borderTop": "1px solid rgba(255,255,255,0.2)", "fontSize": "11px", "opacity": "0.8", "textAlign": "center", "--chart-color-palette": "default"}}>{"© 2026 BESSER. All rights reserved."}</p>
      </nav>
      <main id="im8w5n" style={{"flex": "1", "padding": "40px", "overflowY": "auto", "background": "#f5f5f5", "--chart-color-palette": "default"}}>
        <h1 id="i7lwdy" style={{"marginTop": "0", "color": "#333", "fontSize": "32px", "marginBottom": "10px", "--chart-color-palette": "default"}}>{"Evenement"}</h1>
        <p id="i634ph" style={{"color": "#666", "marginBottom": "30px", "--chart-color-palette": "default"}}>{"Manage Evenement data"}</p>
        <TableBlock id="table-evenement-5" styles={{"width": "100%", "minHeight": "400px", "--chart-color-palette": "default"}} title="Evenement List" options={{"showHeader": true, "stripedRows": false, "showPagination": true, "rowsPerPage": 5, "actionButtons": true, "columns": [{"label": "Nom", "column_type": "field", "field": "nom", "type": "str", "required": true}, {"label": "Description", "column_type": "field", "field": "description", "type": "str", "required": true}, {"label": "NbParticipantsPrevus", "column_type": "field", "field": "nbParticipantsPrevus", "type": "int", "required": true}, {"label": "EmailReferent", "column_type": "field", "field": "emailReferent", "type": "str", "required": true}, {"label": "DateDebut", "column_type": "field", "field": "dateDebut", "type": "date", "required": true}, {"label": "DateFin", "column_type": "field", "field": "dateFin", "type": "date", "required": true}], "formColumns": [{"column_type": "field", "field": "emailReferent", "label": "emailReferent", "type": "str", "required": true, "defaultValue": null}, {"column_type": "field", "field": "dateDebut", "label": "dateDebut", "type": "date", "required": true, "defaultValue": null}, {"column_type": "field", "field": "dateFin", "label": "dateFin", "type": "date", "required": true, "defaultValue": null}, {"column_type": "field", "field": "nom", "label": "nom", "type": "str", "required": true, "defaultValue": null}, {"column_type": "field", "field": "description", "label": "description", "type": "str", "required": true, "defaultValue": null}, {"column_type": "field", "field": "nbParticipantsPrevus", "label": "nbParticipantsPrevus", "type": "int", "required": true, "defaultValue": null}, {"column_type": "lookup", "path": "reservation", "field": "reservation", "lookup_field": "dateDebut", "entity": "Reservation", "type": "list", "required": false}]}} dataBinding={{"entity": "Evenement", "endpoint": "/evenement/"}} />
      </main>
    </div>    </div>
  );
};

export default Evenement;
