SELECT
  ci.item_code,
  ci.technician,
  DATEDIFF(cis.setup_date, ci.received_date) AS turnaround_days
FROM
  `tabClarinet Intake` ci
JOIN
  `tabInstrument Inspection` insp ON ci.name = insp.clarinet_intake
JOIN
  `tabClarinet Initial Setup` cis ON insp.name = cis.inspection
WHERE
  cis.docstatus = 1