SELECT
  ci.item_code,
  ci.technician,
  DATEDIFF(cis.setup_date, ci.received_date) AS turnaround_days
FROM
  `tabClarinet Intake` ci
JOIN
  `tabClarinet Inspection` insp ON ci.name = insp.intake
JOIN
  `tabClarinet Initial Setup` cis ON insp.name = cis.inspection
WHERE
  cis.docstatus = 1