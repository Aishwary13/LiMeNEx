graph [
  directed 1
  node [
    id 0
    label "Glycerol3phosphate(ii)"
  ]
  node [
    id 3
    label "GPAT2"
  ]
  node [
    id 4
    label "GPAT3"
  ]
  node [
    id 5
    label "LPIN2"
  ]
  node [
    id 6
    label "DAG(i)"
  ]
  node [
    id 7
    label "Dietary TAG(ii)"
  ]
  node [
    id 8
    label "PNLIP"
  ]
  node [
    id 10
    label "DAG(ii)"
  ]
  node [
    id 11
    label "DGAT1"
  ]
  node [
    id 12
    label "TAG(i)"
  ]
  edge [
    source 0
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
    source 7
    target 8
  ]
  edge [
    source 8
    target 6
  ]
  edge [
    source 10
    target 11
  ]
  edge [
    source 11
    target 12
  ]
]
