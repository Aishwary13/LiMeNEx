graph [
  directed 1
  node [
    id 0
    label "Citrate(ii)"
  ]
  node [
    id 1
    label "ACLY"
    Uniprot_ID "P53396"
  ]
  node [
    id 2
    label "Acetyl-CoA(i)"
  ]
  node [
    id 3
    label "Acetyl-CoA(ii)"
  ]
  node [
    id 4
    label "ACACA"
    Uniprot_ID "Q13085"
  ]
  node [
    id 5
    label "FASN"
    Uniprot_ID "P49327"
  ]
  node [
    id 6
    label "SCD"
    Uniprot_ID "O00767"
  ]
  node [
    id 7
    label "Fatty Acids(i)"
  ]
  edge [
    source 0
    target 1
  ]
  edge [
    source 1
    target 2
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
]
