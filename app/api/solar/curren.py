/api/solar/current:
  get:
    summary: "Get Current Solar Activity"
    responses:
      '200':
        description: "Successful solar data retrieval"
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/SolarActivity'
            examples:
              normal_activity:
                summary: "Normal solar activity"
                value:
                  sunspot_number: 86
                  solar_flux: 113
                  flare_activity: 2
      '500':
        description: "Server error"
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Error'
