{
  "hookInstance": "d1577c69-dfbe-44ad-ba6d-3e05e953b2ea",
  "hook": "order-sign",
  "fhirServer": "https://fhir.example.com",
  "user": "Practitioner/example",
  "context": {
    "patientId": "1288992",
    "medications": [
      {
        "resourceType": "MedicationRequest",
        "id": "medrx001",
        "status": "draft",
        "medicationCodeableConcept": {
          "coding": [
            {
              "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
              "code": "857001",
              "display": "Acetaminophen 325 MG / Hydrocodone Bitartrate 10 MG Oral Tablet"
            }
          ]
        },
        "dosageInstruction": [
          {
            "text": "Take 1 tablet by mouth every 4 hours as needed",
            "timing": { "repeat": { "frequency": 6, "period": 1, "periodUnit": "d" } },
            "doseQuantity": { "value": 10, "unit": "mg", "system": "http://unitsofmeasure.org", "code": "mg" }
          }
        ],
        "patient": { "reference": "Patient/example" }
      }
    ]
  },
  "prefetch": {
    "patient": {
      "resourceType": "Patient",
      "id": "1288992",
      "birthDate": "2020-06-15",
      "name": [{ "family": "Smith", "given": ["Jamie"] }]
    }
  },
  "extension": {
    "my-org.preferences": {
      "age-measurement-unit": "months",
      "uiHints": {
        "suppressLinks": false,
        "preferredSeverity": "warning"
      },
      "requestOrigin": "order-entry-screen"
    }
  }
}

----

{
  "hookInstance": "a3f5b8e2-9c4d-4b6a-8d9f-2b7c6e5f1a23",
  "hook": "order-select",
  "fhirServer": "https://fhir.example.org",
  "user": "Practitioner/12345",
  "context": {
    "patientId": "patient-98765",
    "encounterId": "encounter-4321",
    "selections": [
      "MedicationRequest/medreq-001",
      "ServiceRequest/svc-010"
    ],
    "draftOrders": {
      "resourceType": "Bundle",
      "type": "collection",
      "entry": [
        {
          "resource": {
            "resourceType": "MedicationRequest",
            "id": "medreq-001",
            "status": "draft",
            "medicationCodeableConcept": {
              "coding": [
                {
                  "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
                  "code": "5612",
                  "display": "Amoxicillin 500 mg oral capsule"
                }
              ]
            },
            "dosageInstruction": [
              {
                "text": "Take 1 capsule by mouth every 8 hours for 7 days",
                "timing": {
                  "repeat": {
                    "frequency": 3,
                    "period": 1,
                    "periodUnit": "d"
                  }
                },
                "doseAndRate": [
                  {
                    "doseQuantity": {
                      "value": 500,
                      "unit": "mg"
                    }
                  }
                ]
              }
            ],
            "subject": {
              "reference": "Patient/patient-98765"
            }
          }
        },
        {
          "resource": {
            "resourceType": "ServiceRequest",
            "id": "svc-010",
            "status": "draft",
            "code": {
              "coding": [
                {
                  "system": "http://loinc.org",
                  "code": "47527-7",
                  "display": "Complete blood count panel"
                }
              ]
            },
            "subject": {
              "reference": "Patient/patient-98765"
            }
          }
        }
      ]
    }
  },
  "prefetch": {
    "patient": {
      "resourceType": "Patient",
      "id": "patient-98765",
      "birthDate": "1980-03-22",
      "name": [
        {
          "family": "Doe",
          "given": [
            "Alex"
          ]
        }
      ]
    }
  },
  "extension": {
    "my-org.orderPreferences": {
      "preferredFormularyTier": "tier-2",
      "allowSubstitutions": true,
      "uiHints": {
        "highlightInteractions": true,
        "suppressNonActionableWarnings": false
      },
      "requestOrigin": "outpatient-ordering",
      "maxResponseLatencyMs": 1200
    }
  }
}

----

### order-select request example including a CommunicationRequest resource

```json
{
  "hookInstance": "f2a9d4b6-7b3c-49e1-9c7a-0b6e4c2d9f11",
  "hook": "order-select",
  "fhirServer": "https://fhir.example.org",
  "user": "Practitioner/12345",
  "context": {
    "patientId": "patient-98765",
    "encounterId": "encounter-4321",
    "selections": [
      "MedicationRequest/medreq-001",
      "CommunicationRequest/commreq-002"
    ],
    "draftOrders": {
      "resourceType": "Bundle",
      "type": "collection",
      "entry": [
        {
          "resource": {
            "resourceType": "MedicationRequest",
            "id": "medreq-001",
            "status": "draft",
            "medicationCodeableConcept": {
              "coding": [
                {
                  "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
                  "code": "582620",
                  "display": "Amoxicillin 500 mg oral capsule"
                }
              ]
            },
            "dosageInstruction": [
              {
                "text": "Take 1 capsule by mouth every 8 hours for 7 days",
                "timing": {
                  "repeat": {
                    "frequency": 3,
                    "period": 1,
                    "periodUnit": "d"
                  }
                },
                "doseAndRate": [
                  {
                    "doseQuantity": {
                      "value": 500,
                      "unit": "mg"
                    }
                  }
                ]
              }
            ],
            "subject": {
              "reference": "Patient/patient-98765"
            },
            "encounter": {
              "reference": "Encounter/encounter-4321"
            }
          }
        },
        {
          "resource": {
            "resourceType": "CommunicationRequest",
            "id": "commreq-002",
            "status": "active",
            "subject": {
              "reference": "Patient/patient-98765"
            },
            "encounter": {
              "reference": "Encounter/encounter-4321"
            },
            "payload": [
              {
                "contentString": "Please notify the primary care physician that a new antibiotic was ordered."
              }
            ],
            "recipient": [
              {
                "reference": "Practitioner/pcp-100"
              },
              {
                "reference": "HealthcareService/clinic-55"
              }
            ],
            "priority": "routine",
            "authoredOn": "2025-09-21T08:15:00Z"
          }
        }
      ]
    }
  },
  "prefetch": {
    "patient": {
      "resourceType": "Patient",
      "id": "patient-98765",
      "birthDate": "1980-03-22",
      "name": [
        {
          "family": "Doe",
          "given": [
            "Alex"
          ]
        }
      ]
    }
  },
  "extension": {
    "my-org.orderPreferences": {
      "notifyRecipients": true,
      "communicationPriority": "routine",
      "requestOrigin": "order-entry-screen"
    }
  }
}
```

---

#### Notes
- **selections** lists the newly selected order resource ids; here it includes a CommunicationRequest id.
- **draftOrders** contains a Bundle of the unsigned/draft orders including the CommunicationRequest resource.
- The CDS Service can inspect the CommunicationRequest payload, recipient, and priority to tailor suggestions or create actions (for example, adding a suggestion to send the communication or modify its content).
- Include the extension schema in your discovery metadata so clients know the expected extension shape.

----

### CDS Service Discovery Response

```json
{
  "services": [
    {
      "id": "my-org-order-service",
      "hook": "order-select",
      "title": "MyOrg Order Assistant",
      "description": "Provides suggestions and actions for selected draft orders, including handling CommunicationRequest resources and ordering preferences.",
      "prefetch": {
        "patient": "Patient/{{context.patientId}}"
      },
      "scopes": [
        "launch",
        "patient/Patient.read",
        "user/Practitioner.read"
      ],
      "metadata": {
        "author": "MyOrg CDS Team",
        "version": "1.0.0"
      },
      "extensions": {
        "my-org.orderPreferences": {
          "description": "Client-sent preferences and UI hints used to adjust service behavior for order-select interactions.",
          "example": {
            "notifyRecipients": true,
            "communicationPriority": "routine",
            "requestOrigin": "order-entry-screen",
            "preferredFormularyTier": "tier-2",
            "allowSubstitutions": true,
            "uiHints": {
              "highlightInteractions": true,
              "suppressNonActionableWarnings": false
            },
            "maxResponseLatencyMs": 1200
          },
          "schema": {
            "type": "object",
            "properties": {
              "notifyRecipients": {
                "type": "boolean"
              },
              "communicationPriority": {
                "type": "string"
              },
              "requestOrigin": {
                "type": "string"
              },
              "preferredFormularyTier": {
                "type": "string"
              },
              "allowSubstitutions": {
                "type": "boolean"
              },
              "uiHints": {
                "type": "object",
                "properties": {
                  "highlightInteractions": {
                    "type": "boolean"
                  },
                  "suppressNonActionableWarnings": {
                    "type": "boolean"
                  },
                  "suppressLinks": {
                    "type": "boolean"
                  },
                  "preferredSeverity": {
                    "type": "string"
                  }
                },
                "additionalProperties": true
              },
              "maxResponseLatencyMs": {
                "type": "integer"
              }
            },
            "additionalProperties": true
          }
        }
      }
    }
  ]
}
```

Notes
- The discovery response lists the service that handles the order-select hook and exposes a namespaced extension key "my-org.orderPreferences" describing expected shape and an example.
- Clients can use this metadata to know which extension names and JSON structure the CDS Service supports.

----


### order-select request with CommunicationRequest no extension

```json
{
  "hookInstance": "b4c3f9a1-6d2e-4f8b-9a12-e7d6c5b4a321",
  "hook": "order-select",
  "fhirServer": "https://fhir.example.org",
  "user": "Practitioner/12345",
  "context": {
    "patientId": "patient-98765",
    "encounterId": "encounter-4321",
    "selections": [
      "MedicationRequest/medreq-001",
      "CommunicationRequest/commreq-002"
    ],
    "draftOrders": {
      "resourceType": "Bundle",
      "type": "collection",
      "entry": [
        {
          "resource": {
            "resourceType": "MedicationRequest",
            "id": "medreq-001",
            "status": "draft",
            "medicationCodeableConcept": {
              "coding": [
                {
                  "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
                  "code": "582620",
                  "display": "Amoxicillin 500 mg oral capsule"
                }
              ]
            },
            "dosageInstruction": [
              {
                "text": "Take 1 capsule by mouth every 8 hours for 7 days",
                "timing": {
                  "repeat": {
                    "frequency": 3,
                    "period": 1,
                    "periodUnit": "d"
                  }
                },
                "doseAndRate": [
                  {
                    "doseQuantity": {
                      "value": 500,
                      "unit": "mg"
                    }
                  }
                ]
              }
            ],
            "subject": {
              "reference": "Patient/patient-98765"
            },
            "encounter": {
              "reference": "Encounter/encounter-4321"
            }
          }
        },
        {
          "resource": {
            "resourceType": "CommunicationRequest",
            "id": "commreq-002",
            "status": "active",
            "subject": {
              "reference": "Patient/patient-98765"
            },
            "encounter": {
              "reference": "Encounter/encounter-4321"
            },
            "payload": [
              {
                "contentString": "Please notify the primary care physician that a new antibiotic was ordered."
              }
            ],
            "recipient": [
              {
                "reference": "Practitioner/pcp-100"
              },
              {
                "reference": "HealthcareService/clinic-55"
              }
            ],
            "priority": "routine",
            "authoredOn": "2025-09-21T08:15:00Z"
          }
        }
      ]
    }
  },
  "prefetch": {
    "patient": {
      "resourceType": "Patient",
      "id": "patient-98765",
      "birthDate": "1980-03-22",
      "name": [
        {
          "family": "Doe",
          "given": [
            "Alex"
          ]
        }
      ]
    }
  }
}
```

---

{
  "services": [
    {
      "id": "my-org-order-service",
      "hook": "order-select",
      "title": "MyOrg Order Assistant",
      "description": "Provides suggestions and actions for selected draft orders, including handling CommunicationRequest resources.",
      "prefetch": {
        "patient": "Patient/{{context.patientId}}",
        "draftOrders": "Bundle?patient={{context.patientId}}&status=draft"
      },
      "scopes": [
        "launch",
        "patient/Patient.read",
        "user/Practitioner.read",
        "patient/MedicationRequest.read",
        "patient/ServiceRequest.read",
        "patient/CommunicationRequest.read"
      ],
      "metadata": {
        "author": "MyOrg CDS Team",
        "version": "1.0.0",
        "supportedResources": [
          "MedicationRequest",
          "ServiceRequest",
          "CommunicationRequest"
        ]
      }
    }
  ]
}