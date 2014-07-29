<html>
<head>
    <style type="text/css">
        ${css}

        .right {
            text-align: right;
        }

        table.cell_extended {
            border-collapse: collapse;
        }

        .cell_extended td {
            border: 1px solid gray;
            margin: 0px;
        }

        .under_line {
            border-bottom: 1px solid black;
        }

        .product_line td {
            border-bottom: 1px dotted lightgray;
        }
    </style>
    <title>Price List.pdf</title>
</head>
   <body>
%for plist in objects:
    <%
    active_version = get_active_version(plist)
    %>
        <table  width="100%">
            <tr>
                <td style="text-align:center;"><br/><br/><br/>
                    <h2><b> Price List</b></h2>
                </td>
            </tr>
        </table>

        <table width="100%" class="cell_extended">
            <tr>
                <td style="text-align:center;" class="cell_extended">
                <b>${ _('Price List Name') }</b>
                </td>
                <td style="text-align:center;" class="cell_extended">
                <b>${ _('Currency') }</b>
                </td>
                <td style="text-align:center;" class="cell_extended">
                <b>${ _('Start Date') }</b>
                </td>
                <td style="text-align:center;" class="cell_extended">
                <b>${ _('End Date') }</b>
                <td style="text-align:center;" class="cell_extended">
                <b>${ _('Printing Date') }</b>
                </td>
                </td>
            </tr>
            <tr>
                <td style="text-align:center;" class="cell_extended">   
                ${active_version.name}
                </td>
                <td style="text-align:center;" class="cell_extended">
                ${plist.currency_id.name}
                </td>
                <td style="text-align:center;" class="cell_extended">
                ${active_version.date_start}
                </td>
                <td style="text-align:center;" class="cell_extended">
                ${active_version.date_end}
                </td>
                <td style="text-align:center;" class="cell_extended">
                ${formatLang(time.strftime('%Y-%m-%d'), date=True)}
                </td>
            </tr>
        </table>

        <table width="100%" class="under_line">
            <tr><br/>
                <td width="60%"><b>
                ${ _('Description') }</b>
                </td>
                <td width="20%" class="right">
                  <b>${ _("Min Qty") }
                </td>
                <td width="20%" class="right">
                  <b>${ _("Price") }</b>
                </td>
            </tr>
        </table>

        <table width="100%">
       %for (category, products) in get_price_lines(plist, active_version):
                <tr>
                    <td class="under_line" width="60%" ><br/>
                     <b>${ category }</b>
                    </td> 
                     <td width="40%" colspan="2" />
                </tr>
            %for p in products:
                <tr class="product_line">
                    <td width="60%">
                        ${ p['code'] and '[' + p['code'] + '] ' or '' } ${ p['name'] }
                    </td>
                    <td class="right" width="20%" >
                        ${ p["min_qty"] and p["min_qty"] or '' }
                    </td>
                    <td class="right price" width="20%">
                        <b>${ p["price"] }</b>
                    </td>
                </tr>
            %endfor
       %endfor
        </table>
       <p style="page-break-after:always">
        </p>
%endfor
</body>
</html>
