$headers = @{}
$headers.Add("Content-Type","application/json")
$headers.Add("Accept","application/json")
$headers.Add("token","234a2526-11c6-4a72-b1b6-2eea0080604c")
$body = @"
[
  {
    "target": {
      "x": 0,
      "y": 150,
      "z": 50
    },
    "type": "moveTo"
  },
  {
    "target": {
      "x": 0,
      "y": 150,
      "z": 0
    },
    "type": "moveTo"
  },
  {
    "target": {
      "x": 0,
      "y": 150,
      "z": 130
    },
    "type": "moveTo"
  },
  {
    "target": {
      "x": 0,
      "y": 150,
      "z": 50
    },
    "type": "moveTo"
  },
  { "type": "grab"},
  {
    "target": {
      "x": -150,
      "y": 130,
      "z": 50
    },
    "type": "moveTo"
  },
  {
    "target": {
      "x": 150,
      "y": 130,
      "z": 50
    },
    "type": "moveTo"
  },
  { "type": "release" },
  {
    "target": {
      "x": 0,
      "y": 150,
      "z": -50
    },
    "type": "moveTo"
  },
  {
    "target": {
      "x": 0,
      "y": 100,
      "z": -50
    },
    "type": "moveTo"
  },
  {
    "target": {
      "x": 0,
      "y": 173,
      "z": 0
    },
    "type": "moveTo"
  }
]
"@


Invoke-WebRequest -method POST -headers $headers -Body $body -Uri 'http://192.168.1.253:8080/Avanade.meArm/1.0.0/arm/00006415121314/operate'