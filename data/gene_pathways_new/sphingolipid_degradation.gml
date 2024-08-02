graph [
  directed 1
  node [
    id 0
    label "Ceramide(ii)"
  ]
  node [
    id 1
    label "ACER1"
    Uniprot_ID "Q8TDN7"
  ]
  node [
    id 2
    label "SMPD1"
    Uniprot_ID "P17405"
  ]
  node [
    id 3
    label "UGCG"
    Uniprot_ID "Q16739"
  ]
  node [
    id 4
    label "Cholesterol(i)"
  ]
  node [
    id 5
    label "Glucosylceramide(i)"
  ]
  node [
    id 6
    label "SGPP1"
    Uniprot_ID "Q9BX95"
  ]
  node [
    id 7
    label "SGPL1"
    Uniprot_ID "O95470"
  ]
  node [
    id 8
    label "ALDH3A2"
    Uniprot_ID "P51648-2"
  ]
  node [
    id 9
    label "Hexadecenal(i)"
  ]
  edge [
    source 0
    target 1
  ]
  edge [
    source 0
    target 2
  ]
  edge [
    source 0
    target 3
  ]
  edge [
    source 1
    target 6
  ]
  edge [
    source 2
    target 4
  ]
  edge [
    source 3
    target 5
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
]
