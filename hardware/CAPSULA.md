# Capsula del sensor y vaina del ESP32

Contexto completo y paso a paso para diseñar las dos piezas en Fusion 360. Sirve tambien para pasarselo a otra IA. Medidas en mm. Actualizado 23/10/2026: la Pieza B se agranda porque la primera impresion no entraba (ver seccion 5).

## 1. Proyecto

Paleta de ping pong con un sensor MPU-6500 (acelerometro + giroscopio) y una ESP32-S3 que reconoce golpes con TinyML y manda los resultados por BLE a una app en el celular. Todo el hardware va en el pomo (el extremo del mango). Se alimenta con un powerbank en el bolsillo, con un cable USB-C que sube por el brazo.

Son dos piezas impresas en **PETG**:

- **Pieza A, capsula del sensor:** un capuchon que se calza en el extremo del mango y tapa el sensor.
- **Pieza B, vaina del ESP32:** encastra abajo de la Pieza A y prolonga el mango. Adentro va la placa.

## 2. Como se monta

De la paleta hacia abajo:

1. **Mango de madera.** La base del pomo es plana y ahi va el sensor, pegado con cinta bifaz VHB.
2. **Pieza A.** Sus paredes envuelven el mango. El piso tiene un bolsillo donde queda el sensor, un techo de 1,2 mm con el hueco de los cables y, abajo, una pestaña en forma de aro.
3. **Pieza B.** Una tapa con un teton que entra en el aro de la Pieza A, y debajo el cuerpo con el ESP32. El USB-C queda en la punta de abajo.

```
      |  mango  |
   +--+---------+--+
   |  |         |  |   paredes de A (envuelven el mango)
   |  |=========|  |   base del pomo (madera)
   |  |[sensor] |  |   bolsillo de A, el sensor pegado a la madera
   |  +---  ----+  |   techo de 1,2 con el hueco de cables
   +--+  aro de A  +-+
     [ teton de B  ]
   +-----------------+  tapa de B (al ras de la pestaña)
       |  ESP32  |      cuerpo de B
       |         |
       +--[USB]--+
```

En Fusion, la Pieza A esta dibujada **al reves que en uso**: la cavidad donde entra el mango mira hacia arriba y la pestaña queda abajo.

### Decisiones que no hay que "corregir"

- **El bolsillo se abre hacia la cavidad del mango,** no hacia la pestaña. El sensor esta pegado a la base del pomo y el bolsillo lo tapa.
- **El sensor no lo sostiene la capsula.** Va pegado a la madera para que el golpe le llegue directo: es clave para detectar el impacto por jerk. El plastico no lo tiene que tocar.
- **Las paredes interiores de la Pieza A son rectas,** aunque el mango se afine. Si copiaran la pendiente, la base del mango no pasaria por la boca, porque el PETG no cede. La luz que queda arriba se tapa con cinta de pintor en el mango.
- **La Pieza B entra en el aro con un teton,** no con un collar por afuera. Asi queda al ras de la pestaña y no agrega 2 mm por lado.

## 3. Medidas de los componentes

| Componente | Medida |
| --- | --- |
| Base del mango | 33 × 23. A 19 mm de la base: 32 × 23 |
| Placa del sensor MPU-6500 | 26 × 16, 1,6 de espesor. Componente mas alto: 1,45 (el regulador) |
| Cinta VHB | 1,0 |
| Cinta de pintor debajo de la VHB | 0,15 |
| Alto del sensor sobre la madera | 4,2 (0,15 + 1 + 1,6 + 1,45) |
| Cables del sensor | 7 cables pelados, de unos 1,5 de diametro: VCC, GND, SCL, SDA, AD0, NCS e INT. Salen de la tira de pines, que esta en un lado largo de la placa |
| ESP32-S3 (GOOUUU ESP32-S3-CAM) | Medido con calibre el 23/10: **28,1** de ancho maximo (con los plasticos amarillos de los pines), **67,2** de largo y **18,1** de espesor, de la punta de los pines a la lente de la camara. La camara queda puesta (no se puede sacar). De la punta de los pines al borde de arriba de los USB-C: **12,3**. Los dos USB-C estan en la punta opuesta al modulo metalico (ahi va la antena), uno a cada lado del centro. Se usa el **OTG** |

## 4. Pieza A: capsula del sensor

### Medidas

| Parte | Medida | Por que |
| --- | --- | --- |
| Interior de las paredes | **33,4 × 23,4**, recto, con la forma redondeada del mango | La base del mango mas 0,2 de juego por lado |
| Espesor de pared | **2** como minimo | |
| Alto de pared | **19**, desde la cara de abajo del piso hasta el borde, sin contar la pestaña | Quedan unos 12 de agarre sobre el mango (19 − 6,7) |
| Piso | **6,7** | 5,5 de bolsillo + 1,2 de techo |
| Bolsillo del sensor | **28 × 18**, **5,5** de profundidad, centrado, abierto hacia la cavidad | La placa de 26 × 16 se pega a mano y necesita juego. Quedan 1,3 de aire sobre el sensor |
| Hueco de cables | **25 × 4,5**, atraviesa el techo | Entran los 7 cables en fila. Quedan 1,5 de apoyo a cada lado del bolsillo |
| Pestaña (aro) | Exterior **39,45 × 29,2**, interior **35,85 × 25,2**, alto **2,3** + chamfer de **0,43** abajo | Ya esta hecha |

Desde el centro de la pieza, el hueco de cables va de unos 4,2 a 8,65 mm hacia un lado largo. Son valores aproximados, sacados de capturas.

### Paso a paso

1. **Paredes:** el interior de 33,4 × 23,4, recto y sin pendiente. Espesor de 2 mm. Alto de 19 mm.
2. **Piso:** 6,7 mm de espesor.
3. **Bolsillo:** boceto sobre la cara del piso que mira a la cavidad (la que toca la base del pomo). Rectangulo de 28 × 18, centrado. **Extrude → Cut, 5,5 mm.**
4. **Hueco de cables:** boceto sobre el fondo del bolsillo. Rectangulo de 25 × 4,5, centrado a lo largo, con el lado largo pegado al borde del bolsillo del lado donde va la tira de pines del sensor. **Extrude → Cut, Extent: All.** Con Distance, si despues cambia el piso, el hueco deja de atravesar.
5. **Pestaña:** el aro con las medidas de la tabla. Ya esta hecha.
6. **Refuerzos:**
   - Pared con pestaña, por afuera: **fillet de 1 mm**. Ya esta hecho.
   - Pared con piso, por adentro: **fillet de 0,5 mm como maximo** si el borde de la base del mango es vivo. Si es mas grande, la base del mango no llega a apoyar en el piso.
   - Esquinas verticales del bolsillo: fillet de 1 a 2 mm. Es opcional.
   - Borde del hueco, del lado de afuera: **chamfer de 0,5 mm**, para no cortar el aislante de los cables.
7. **Comprobar:** Section Analysis por el medio y otro que pase por el hueco. Despues ocultarlos con el ojito de la carpeta Analysis.

## 5. Pieza B: vaina del ESP32

**La primera impresion no entro.** Tenia un interior de 27 × 15, pensado para una placa de 26 × 12 medida con regla. Con calibre la placa da 28,1 de ancho (los plasticos de los pines sobresalen) y 18,1 de espesor (la camara sobresale arriba). Las medidas de abajo ya estan corregidas, con margen de sobra: lo que quede flojo se rellena con goma EVA o cinta. El largo no cambia.

Tiene tres partes:

- una **tapa** de 2 mm con el mismo contorno exterior que la pestaña de la Pieza A, para que quede al ras;
- un **teton** que entra en el aro;
- un **cuerpo** angosto donde va la placa, con el USB-C abajo.

La placa entra por arriba, deslizando: en el armado, la vaina sube desde abajo y la placa, que cuelga de los cables del sensor, entra por la abertura de la tapa.

### Medidas

| Parte | Medida | Por que |
| --- | --- | --- |
| Tapa | Contorno exterior de la pestaña (**39,45 × 29,2**), **2** de espesor | Al ras de la Pieza A |
| Teton | Contorno interior del aro menos 0,2 por lado (**35,45 × 24,8**), alto **p − 0,3** | Entra sin forzar. Los 0,3 de diferencia hacen que la tapa apoye en el aro y no el teton en el techo |
| Cuerpo, exterior | **35 × 25**, esquinas r = 2, **78** de largo, **centrado** | Paredes y fondo de 2. Bajo la tapa de 39,45 × 29,2 sobran unos 2,2 por lado |
| Cuerpo, interior | **31 × 21**, el mismo largo que antes | Placa de 28,1 × 18,1: unos 1,5 de juego por lado (alcanza aunque la impresora achique unas decimas y deja lugar para el estaño de los cables). A lo largo quedan unos 12 libres arriba para que los cables se doblen |
| Ranura de los USB | **26 × 13**, centrada en el fondo | Deja a la vista los dos USB-C: si la placa no arranca por el OTG se usa el otro sin reimprimir. Cubre las dos fichas (12 × 6,5 cada una) aunque la placa quede corrida 1,5 para cualquier lado |

**p** es la profundidad del rebaje dentro del aro de la Pieza A: de la cara de abajo del aro a la cara de abajo del techo. Hay que medirla.

**El cuerpo ya no va corrido.** En la primera version se corria 2 mm hacia el hueco de cables porque un interior de 15 no lo cubria. El de 21 centrado llega a 10,5 del centro y el hueco solo hasta 8,65: queda adentro. A lo largo el interior mide 31 y el hueco 25.

**Ranura en el espesor:** el centro de los USB-C queda a 12,3 − 1,6 = 10,7 de la punta de los pines. Con la placa centrada (1,45 de juego de cada lado) eso es 1,65 corrido del centro hacia el lado de la camara. La ranura de 13 centrada va de 4 a 17 desde la pared de los pines, y las fichas, con la placa movida 1,5 para cualquier lado, ocupan de 7,5 a 17. Entra.

**Paredes del teton:** el interior lo atraviesa, asi que quedan de 2,2 y 1,9 mm ((35,45 − 31) / 2 y (24,8 − 21) / 2).

### Como quedo en el archivo de Fusion (23/10)

El archivo de Tomas (`paleta-ping-pong.f3d`) no tiene el teton que describe esta guia: la tapa es una **placa de 4 mm** (dos escalones de 2, el de arriba 0,2 mas chico por lado y con chamfer de 1 en el borde) que apoya plana contra el aro de la Pieza A. Por eso el chamfer no se toco. Los cambios hechos en la version `paleta-ping-pong-v2.f3d`:

| Cota | Antes | Ahora |
| --- | --- | --- |
| Boceto14 (cuerpo): d59 × d60 | 31 × 19 | **35 × 25** |
| Boceto14: d65 (origen → borde del cuerpo) | 7,5 | **12,1** |
| Boceto15 (interior): d68 × d69 | 27 × 15 | **31 × 21** |
| Boceto15: d70 (borde del interior → origen) | 9,5 | **10,9** |
| Boceto16 (agujero USB): d73 × d74 | 14 × 8 | **26 × 13** (ranura) |
| Boceto16: d82, d81 (posicion) | 11,5 y 6 | **17,5 y 12,5** |
| Fillet4 (union cuerpo-placa) | 2 | **1,5**, rehecho: con el cuerpo de 25 a la placa le quedan ~1,9 al costado |

- Todo queda centrado en x = 0 e y = −0,4, que es el centro de la placa (va de −14,77 a 14,03). Los bocetos 14 y 15 no estaban fijos a lo ancho y se movieron a mano al centro.
- Resultado medido en el modelo: cuerpo de −17,5 a 17,5 por −12,9 a 12,1; interior de 31 × 21 desde la cara de arriba de la placa hasta 2,3 del fondo (77,7 de largo); ranura de x −13 a 13 por y −6,9 a 6,1.
- El aviso de "base mango" (un lienzo con una cara perdida) ya estaba antes y no afecta a la vaina.

### Paso a paso

Se hace en el **mismo archivo que la Pieza A, como un cuerpo nuevo**, para poder proyectar los contornos de la pestaña.

0. **Medir p** con **Inspect → Measure**. Fijarse tambien si la esquina interna del aro tiene fillet y de que radio.
1. **Tapa.** Boceto sobre la cara de abajo del aro. **Project** del contorno exterior de la pestaña. **Extrude 2 mm** hacia abajo, alejandose de la Pieza A, como **New Body**. Nombrarlo `vaina`.
2. **Teton.** Boceto sobre la misma cara. **Project** del contorno interior del aro y **Offset de 0,2 mm hacia adentro**. **Extrude** de ese perfil hacia la Pieza A, adentro del rebaje, con un alto de **p − 0,3**. Operacion **Join**, solo con el cuerpo `vaina`.
3. **Chamfer de 0,5 mm** en el borde de arriba del teton, por afuera, para que no choque con el fillet de la esquina interna del aro. Si ese fillet es mas grande, el chamfer tiene que ser por lo menos del mismo tamaño, pero no mas de 1 mm: la pared del teton mide 1,9.
4. **Cuerpo.** Boceto sobre la cara de abajo de la tapa. Rectangulo de **35 × 25** con esquinas r = 2, **centrado** en los dos sentidos. **Extrude 78 mm** hacia abajo, **Join**.
5. **Interior.** Boceto sobre la cara de arriba del teton. Rectangulo de **31 × 21**, concentrico con el del paso 4. **Extrude → Cut** de **(p − 0,3) + 78 mm**. Atraviesa el teton y la tapa, baja por el cuerpo y deja **2 mm de fondo**. Comprobar en un corte que el hueco de la Pieza A caiga entero dentro de esta abertura.
6. **Ranura de los USB.** En la cara de abajo de la vaina, rectangulo de **26 × 13** centrado (el lado de 26 paralelo al de 31 del interior). **Extrude → Cut, Extent: All.**
   - La placa entra con los **pines mirando hacia el lado del hueco de cables**, asi los cables bajan pegados a esa pared y llegan directo a los pines.
   - La ranura deja ver los dos USB-C, asi que no importa de que lado queda el OTG.
7. **Refuerzo:** **fillet de 2 mm** en la union del cuerpo con la cara de abajo de la tapa.
8. **Opcional:** agujerito de **2 a 3 mm** sobre el boton BOOT, para apretarlo con un clip. Otro sobre el LED, si queda tapado.
9. **Comprobar** con Section Analysis y ocultarlo despues.

## 6. Impresion

- Las dos piezas, en **PETG**.
- Segun el laboratorio, la impresora se come unos **0,06 mm** (23/10). Con 1,5 de juego por lado en la Pieza B no hace falta compensarlo.
- **Pieza A:** con la pestaña sobre la cama. El techo del rebaje del aro queda como un puente de unos 25 mm: si el slicer lo marca, activar puentes o soportes.
- **Pieza B:** con el **teton sobre la cama**. No necesita soportes. El fondo queda arriba, como un puente sobre el interior de 21 mm con la ranura en el medio: el PETG lo hace bien.

## 7. Armado

1. Marcar en la base del pomo, con lapiz, el contorno del bolsillo. Sirve apoyar la Pieza A o un papel calcado.
2. Pegar el sensor dentro de esa marca: primero cinta de pintor, despues VHB. Los pines tienen que quedar del lado del hueco de cables.
3. Soldar los 7 cables al sensor y pasarlos por el hueco de la Pieza A.
4. Poner una o dos vueltas de cinta de pintor en el mango y calzar la Pieza A.
5. Soldar los cables a los pines del ESP32: 3V3, GND, GPIO 42, 41, 14, 21 y 1. Largo de cada cable: **unos 35 mm + la distancia de su pin a la punta de arriba de la placa** (la del modulo).
6. Subir la vaina desde abajo, con la placa entrando por la abertura y los USB hacia la ranura. Lo que quede flojo se rellena con goma EVA o cinta, sin tapar la ranura.
7. Dar una vuelta de **cinta aisladora** sobre la union entre las dos piezas. El teton entra poco y por rozamiento puede aflojarse con los golpes.

## 8. Pendientes

- [ ] Medir **p** y el radio del fillet de la esquina interna del aro.
- [x] Posicion del conector OTG a lo ancho: de 4 a 14 mm de un borde de la placa.
- [x] Medir en profundidad la distancia de la punta de los pines al conector: 12,3 al borde de arriba de los USB-C (23/10).
- [x] Medir la placa con calibre: 28,1 × 67,2 × 18,1 con la camara (23/10). La primera Pieza B no entraba.
- [ ] Medir en el ESP32 la distancia de cada pin usado a la punta de arriba, para cortar los cables.
- [ ] Confirmar que el ESP32 arranca alimentado solo por el OTG. Si no, se usa el otro USB-C: la ranura deja ver los dos.
- [ ] Comprobar que la Pieza A tenga los valores de la seccion 4. El 16/10 se perdio una version del archivo.
- [ ] Guardar con **Ctrl+S** despues de cada paso y fijarse en el Data Panel que aparezca la version nueva.
- [ ] Con todo armado, probar el BLE agarrando la paleta como para jugar: la mano queda cerca de la antena.
