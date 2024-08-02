graph [
  directed 1
  node [
    id 0
    label "Citrate"
  ]
  node [
    id 1
    label "ACL"
  ]
  node [
    id 2
    label "Acetyl-CoA(i)"
  ]
  node [
    id 7
    label "Acetyl-CoA(ii)"
  ]
  node [
    id 3
    label "ACC"
  ]
  node [
    id 4
    label "FASN"
  ]
  node [
    id 5
    label "SCD1"
  ]
  node [
    id 6
    label "Fatty Acids"
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
    source 7
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
]
