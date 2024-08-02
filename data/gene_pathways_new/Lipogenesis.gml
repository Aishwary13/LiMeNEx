graph [
  directed 1
  node [
    id 0
    label "Glycerol3phosphate(ii)"
  ]
  node [
    id 1
    label "GPAT2"
    Uniprot_ID "Q6NUI2"
  ]
  node [
    id 2
    label "GPAT3"
    Uniprot_ID "Q53EU6"
  ]
  node [
    id 3
    label "LPIN2"
    Uniprot_ID "Q92539"
  ]
  node [
    id 4
    label "DAG(i)"
  ]
  node [
    id 5
    label "Dietary TAG(ii)"
  ]
  node [
    id 6
    label "PNLIP"
    Uniprot_ID "P16233"
  ]
  node [
    id 7
    label "DAG(ii)"
  ]
  node [
    id 8
    label "DGAT1"
    Uniprot_ID "O75907"
  ]
  node [
    id 9
    label "TAG(i)"
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
    source 2
    target 3
  ]
  edge [
    source 3
    target 4
  ]
  edge [
    source 5
    target 6
  ]
  edge [
    source 6
    target 4
  ]
  edge [
    source 7
    target 8
  ]
  edge [
    source 8
    target 9
  ]
]
