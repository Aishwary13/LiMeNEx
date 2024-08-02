graph [
  directed 1
  node [
    id 0
    label "Lysophosphatidylcholine(ii)"
  ]
  node [
    id 1
    label "GDPD1"
  ]
  node [
    id 2
    label "GDPD5"
  ]
  node [
    id 3
    label "Glycerol3phosphate(i)"
  ]
  node [
    id 4
    label "Lysophosphoinositol(ii)"
  ]
  node [
    id 5
    label "GDE1"
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
    source 4
    target 5
  ]
  edge [
    source 5
    target 3
  ]
]
