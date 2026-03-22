import React from "react";
import { TableBlock } from "../components/runtime/TableBlock";
import { MethodButton } from "../components/MethodButton";

const Centrecongres: React.FC = () => {
  return (
    <div id="page-centrecongres-0">
    <div id="ic21k" style={{"display": "flex", "height": "100vh", "fontFamily": "Arial, sans-serif", "--chart-color-palette": "default"}}>
      <nav id="ia9ah" style={{"width": "250px", "background": "linear-gradient(135deg, #4b3c82 0%, #5a3d91 100%)", "color": "white", "padding": "20px", "overflowY": "auto", "display": "flex", "flexDirection": "column", "--chart-color-palette": "default"}}>
        <h2 id="i5deh" style={{"marginTop": "0", "fontSize": "24px", "marginBottom": "30px", "fontWeight": "bold", "--chart-color-palette": "default"}}>{"BESSER"}</h2>
        <div id="ivlvn" style={{"display": "flex", "flexDirection": "column", "flex": "1", "--chart-color-palette": "default"}}>
          <a id="iruep" style={{"color": "white", "textDecoration": "none", "padding": "10px 15px", "display": "block", "background": "rgba(255,255,255,0.2)", "borderRadius": "4px", "marginBottom": "5px", "--chart-color-palette": "default"}} href="/centrecongres">{"CentreCongres"}</a>
          <a id="i3nh5" style={{"color": "white", "textDecoration": "none", "padding": "10px 15px", "display": "block", "background": "transparent", "borderRadius": "4px", "marginBottom": "5px", "--chart-color-palette": "default"}} href="/gestionnaire">{"Gestionnaire"}</a>
          <a id="ig7kh" style={{"color": "white", "textDecoration": "none", "padding": "10px 15px", "display": "block", "background": "transparent", "borderRadius": "4px", "marginBottom": "5px", "--chart-color-palette": "default"}} href="/elementcentre">{"ElementCentre"}</a>
          <a id="i1m5w" style={{"color": "white", "textDecoration": "none", "padding": "10px 15px", "display": "block", "background": "transparent", "borderRadius": "4px", "marginBottom": "5px", "--chart-color-palette": "default"}} href="/reservation">{"Reservation"}</a>
          <a id="idryk" style={{"color": "white", "textDecoration": "none", "padding": "10px 15px", "display": "block", "background": "transparent", "borderRadius": "4px", "marginBottom": "5px", "--chart-color-palette": "default"}} href="/periodeindisponibilite">{"PeriodeIndisponibilite"}</a>
          <a id="i7i7f" style={{"color": "white", "textDecoration": "none", "padding": "10px 15px", "display": "block", "background": "transparent", "borderRadius": "4px", "marginBottom": "5px", "--chart-color-palette": "default"}} href="/evenement">{"Evenement"}</a>
          <a id="i5e6s" style={{"color": "white", "textDecoration": "none", "padding": "10px 15px", "display": "block", "background": "transparent", "borderRadius": "4px", "marginBottom": "5px", "--chart-color-palette": "default"}} href="/salle">{"Salle"}</a>
          <a id="ikxwq" style={{"color": "white", "textDecoration": "none", "padding": "10px 15px", "display": "block", "background": "transparent", "borderRadius": "4px", "marginBottom": "5px", "--chart-color-palette": "default"}} href="/materiel">{"Materiel"}</a>
          <a id="ii7uh" style={{"color": "white", "textDecoration": "none", "padding": "10px 15px", "display": "block", "background": "transparent", "borderRadius": "4px", "marginBottom": "5px", "--chart-color-palette": "default"}} href="/prestation">{"Prestation"}</a>
        </div>
        <p id="iehkm" style={{"marginTop": "auto", "paddingTop": "20px", "borderTop": "1px solid rgba(255,255,255,0.2)", "fontSize": "11px", "opacity": "0.8", "textAlign": "center", "--chart-color-palette": "default"}}>{"© 2026 BESSER. All rights reserved."}</p>
      </nav>
      <main id="i45jh" style={{"flex": "1", "padding": "40px", "overflowY": "auto", "background": "#f5f5f5", "--chart-color-palette": "default"}}>
        <h1 id="izr16" style={{"marginTop": "0", "color": "#333", "fontSize": "32px", "marginBottom": "10px", "--chart-color-palette": "default"}}>{"CentreCongres"}</h1>
        <p id="i4y3e" style={{"color": "#666", "marginBottom": "30px", "--chart-color-palette": "default"}}>{"Manage CentreCongres data"}</p>
        <TableBlock id="table-centrecongres-0" styles={{"width": "100%", "minHeight": "400px", "--chart-color-palette": "default"}} title="CentreCongres List" options={{"showHeader": true, "stripedRows": false, "showPagination": true, "rowsPerPage": 5, "actionButtons": true, "columns": [{"label": "Nom", "column_type": "field", "field": "nom", "type": "str", "required": true}, {"label": "Adresse", "column_type": "field", "field": "adresse", "type": "str", "required": true}], "formColumns": [{"column_type": "field", "field": "nom", "label": "nom", "type": "str", "required": true, "defaultValue": null}, {"column_type": "field", "field": "adresse", "label": "adresse", "type": "str", "required": true, "defaultValue": null}, {"column_type": "lookup", "path": "elementcentre", "field": "elementcentre", "lookup_field": "nom", "entity": "ElementCentre", "type": "list", "required": false}]}} dataBinding={{"entity": "CentreCongres", "endpoint": "/centrecongres/"}} />
        <div id="ib10k" style={{"marginTop": "20px", "display": "flex", "gap": "10px", "flexWrap": "wrap", "--chart-color-palette": "default"}}>
          <MethodButton id="i43ii" className="action-button-component" style={{"display": "inline-flex", "alignItems": "center", "padding": "6px 14px", "background": "linear-gradient(90deg, #2563eb 0%, #1e40af 100%)", "color": "#fff", "textDecoration": "none", "borderRadius": "4px", "fontSize": "13px", "fontWeight": "600", "letterSpacing": "0.01em", "cursor": "pointer", "border": "none", "boxShadow": "0 1px 4px rgba(37,99,235,0.10)", "transition": "background 0.2s", "--chart-color-palette": "default"}} endpoint="/centrecongres/{centrecongres_id}/methods/getDisponibilites/" label="getDisponibilites" isInstanceMethod={true} instanceSourceTableId="table-centrecongres-0" />
        </div>
      </main>
    </div>    </div>
  );
};

export default Centrecongres;
