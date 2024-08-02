graph [
  directed 1
  node [
    id 0
    label "Fatty Acids(ii)"
  ]
  node [
    id 1
    label "Fatty Acyl-CoA(i)"
  ]
  node [
    id 2
    label "Fatty Acyl-CoA(ii)"
  ]
  node [
    id 3
    label "CPT1A"
    Uniprot_ID "P50416"
  ]
  node [
    id 4
    label "CPT2"
    Uniprot_ID "P23786"
  ]
  node [
    id 5
    label "ACADVL"
    Uniprot_ID "P49748"
  ]
  node [
    id 6
    label "HADHA"
    Uniprot_ID "P40939"
  ]
  node [
    id 7
    label "ACADS"
    Uniprot_ID "P16219"
  ]
  node [
    id 8
    label "ECHS1"
    Uniprot_ID "P30084"
  ]
  node [
    id 9
    label "HADHB"
    Uniprot_ID "P55084"
  ]
  node [
    id 10
    label "Acetyl-CoA(i)"
  ]
  node [
    id 11
    label "HSD17B4"
    Uniprot_ID "P51659"
  ]
  edge [
    source 0
    target 1
  ]
  edge [
    source 2
    target 3
  ]
  edge [
    source 3
    target 4
  ]
  edge [
    source 4
    target 5
  ]
  edge [
    source 5
    target 6
  ]
  edge [
    source 6
    target 7
  ]
  edge [
    source 7
    target 8
  ]
  edge [
    source 8
    target 9
  ]
  edge [
    source 8
    target 11
  ]
  edge [
    source 9
    target 10
  ]
  edge [
    source 11
    target 9
  ]
]
