# Taller Práctico de gRPC

## Objetivo
Aplicar los conceptos aprendidos en la guía mediante ejercicios prácticos progresivos.

---

## Preparación

### 1. Verificar instalación

```bash
cd grpc-basico
npm install
```

### 2. Ejecutar el proyecto base

Terminal 1:
```bash
npm run server
```

Terminal 2:
```bash
npm run client
```

Navega por el menú interactivo y prueba todas las opciones (1-6) para familiarizarte con el proyecto.

---

## Ejercicios Nivel Básico

### Ejercicio 1: Modificar el Servicio Greeter

**Objetivo:** Agregar un nuevo campo al mensaje de saludo.

**Tareas:**

1. Modifica `proto/greeter.proto` para agregar un campo `age` (edad) al mensaje `HelloRequest`:

```protobuf
message HelloRequest {
  string name = 1;
  string language = 2;
  int32 age = 3;  // Agregar este campo
}
```

2. Modifica `server/services/greeterService.ts` en el método `sayHello` para incluir la edad en el mensaje:

```typescript
const response = {
  message: `${greeting}, ${name}! Tienes ${age} años.`,
  timestamp: Date.now(),
};
```

3. Actualiza `client/index.ts` en la función `testSayHello()` para enviar la edad:

```typescript
greeterClient.sayHello(
  { name: 'Juan', language: 'es', age: 25 },
  (error: any, response: any) => {
    // ...
  }
);
```

4. Prueba tu implementación ejecutando servidor y cliente.

**Resultado esperado:**
```
Respuesta: Hola, Juan! Tienes 25 años.
```

---

### Ejercicio 2: Crear un Nuevo RPC en Calculator

**Objetivo:** Agregar una operación de módulo (resto de división).

**Tareas:**

1. Agrega el método en `proto/calculator.proto`:

```protobuf
service Calculator {
  // ... métodos existentes
  rpc Modulo (CalculatorRequest) returns (CalculatorResponse) {}
}
```

2. Implementa el método en `server/services/calculatorService.ts`:

```typescript
export const calculatorService = {
  // ... métodos existentes

  // Módulo
  modulo: (call: any, callback: any) => {
    const { num1, num2 } = call.request;
    console.log(`📐 Modulo: ${num1} % ${num2}`);

    if (num2 === 0) {
      callback(null, {
        result: 0,
        error: 'No se puede calcular módulo por cero',
      });
      return;
    }

    callback(null, {
      result: num1 % num2,
      error: '',
    });
  },
};
```

3. Agrega una prueba en `client/index.ts` dentro de `testCalculator()`:

```typescript
// Módulo
calculatorClient.modulo({ num1: 10, num2: 3 }, (error: any, response: any) => {
  if (error) {
    console.error('Error:', error);
    return;
  }
  console.log('10 % 3 =', response.result);
});
```

4. Ejecuta y prueba.

**Resultado esperado:**
```
10 % 3 = 1
```

---

### Ejercicio 3: Manejar Errores Apropiadamente

**Objetivo:** Implementar manejo de errores usando códigos de estado gRPC.

**Tareas:**

1. Modifica el método `divide` en `server/services/calculatorService.ts`:

```typescript
import * as grpc from '@grpc/grpc-js';

divide: (call: any, callback: any) => {
  const { num1, num2 } = call.request;
  console.log(`➗ Divide: ${num1} ÷ ${num2}`);

  if (num2 === 0) {
    // Usar código de error gRPC apropiado
    callback({
      code: grpc.status.INVALID_ARGUMENT,
      message: 'No se puede dividir por cero',
    });
    return;
  }

  callback(null, {
    result: num1 / num2,
    error: '',
  });
},
```

2. Actualiza el cliente para manejar el error:

```typescript
calculatorClient.divide({ num1: 10, num2: 0 }, (error: any, response: any) => {
  if (error) {
    console.error('Error gRPC:', error.message);
    console.error('Código:', error.code);
    return;
  }
  console.log('10 ÷ 0 =', response.result);
});
```

**Códigos de estado gRPC comunes:**
- `OK` (0): Éxito
- `INVALID_ARGUMENT` (3): Argumento inválido
- `NOT_FOUND` (5): No encontrado
- `ALREADY_EXISTS` (6): Ya existe
- `PERMISSION_DENIED` (7): Permiso denegado
- `UNAUTHENTICATED` (16): No autenticado

---

## Ejercicios Nivel Intermedio

### Ejercicio 4: Crear un Servicio de Lista de Tareas (TODO)

**Objetivo:** Crear un servicio completo desde cero con CRUD básico.

**Tareas:**

1. Crea `proto/todo.proto`:

```protobuf
syntax = "proto3";

package todo;

service TodoService {
  rpc CreateTodo (CreateTodoRequest) returns (Todo) {}
  rpc GetTodo (GetTodoRequest) returns (Todo) {}
  rpc ListTodos (ListTodosRequest) returns (stream Todo) {}
  rpc UpdateTodo (UpdateTodoRequest) returns (Todo) {}
  rpc DeleteTodo (DeleteTodoRequest) returns (DeleteTodoResponse) {}
}

message Todo {
  string id = 1;
  string title = 2;
  string description = 3;
  bool completed = 4;
  int64 created_at = 5;
}

message CreateTodoRequest {
  string title = 1;
  string description = 2;
}

message GetTodoRequest {
  string id = 1;
}

message ListTodosRequest {
  bool show_completed = 1;
}

message UpdateTodoRequest {
  string id = 1;
  string title = 2;
  string description = 3;
  bool completed = 4;
}

message DeleteTodoRequest {
  string id = 1;
}

message DeleteTodoResponse {
  bool success = 1;
  string message = 2;
}
```

2. Crea `server/services/todoService.ts`:

```typescript
import * as grpc from '@grpc/grpc-js';

// Base de datos en memoria
const todos: Map<string, any> = new Map();
let idCounter = 1;

export const todoService = {
  createTodo: (call: any, callback: any) => {
    const { title, description } = call.request;

    const id = `todo-${idCounter++}`;
    const todo = {
      id,
      title,
      description,
      completed: false,
      created_at: Date.now(),
    };

    todos.set(id, todo);
    console.log(`✅ Todo creado: ${id} - ${title}`);
    callback(null, todo);
  },

  getTodo: (call: any, callback: any) => {
    const { id } = call.request;
    const todo = todos.get(id);

    if (!todo) {
      callback({
        code: grpc.status.NOT_FOUND,
        message: `Todo con id ${id} no encontrado`,
      });
      return;
    }

    callback(null, todo);
  },

  listTodos: (call: any) => {
    const { show_completed } = call.request;

    console.log(`📋 Listando todos (completed: ${show_completed})`);

    todos.forEach((todo) => {
      if (show_completed || !todo.completed) {
        call.write(todo);
      }
    });

    call.end();
  },

  updateTodo: (call: any, callback: any) => {
    const { id, title, description, completed } = call.request;
    const todo = todos.get(id);

    if (!todo) {
      callback({
        code: grpc.status.NOT_FOUND,
        message: `Todo con id ${id} no encontrado`,
      });
      return;
    }

    todo.title = title || todo.title;
    todo.description = description || todo.description;
    todo.completed = completed;

    todos.set(id, todo);
    console.log(`🔄 Todo actualizado: ${id}`);
    callback(null, todo);
  },

  deleteTodo: (call: any, callback: any) => {
    const { id } = call.request;

    if (!todos.has(id)) {
      callback({
        code: grpc.status.NOT_FOUND,
        message: `Todo con id ${id} no encontrado`,
      });
      return;
    }

    todos.delete(id);
    console.log(`🗑️  Todo eliminado: ${id}`);
    callback(null, {
      success: true,
      message: `Todo ${id} eliminado correctamente`,
    });
  },
};
```

3. Actualiza `server/index.ts` para incluir el servicio:

```typescript
import { todoService } from './services/todoService';

// ... código existente

const todoPackageDef = protoLoader.loadSync(
  path.join(__dirname, '../proto/todo.proto'),
  packageDefinitionOptions
);
const todoProto = grpc.loadPackageDefinition(todoPackageDef) as any;

// ... después de agregar otros servicios
server.addService(todoProto.todo.TodoService.service, todoService);
```

4. Crea un cliente de prueba en `client/todoClient.ts` (nuevo archivo):

```typescript
import * as grpc from '@grpc/grpc-js';
import * as protoLoader from '@grpc/proto-loader';
import path from 'path';

const PROTO_PATH = path.join(__dirname, '../proto/todo.proto');
const packageDef = protoLoader.loadSync(PROTO_PATH, {
  keepCase: true,
  longs: String,
  enums: String,
  defaults: true,
  oneofs: true,
});

const todoProto = grpc.loadPackageDefinition(packageDef) as any;
const client = new todoProto.todo.TodoService(
  'localhost:50051',
  grpc.credentials.createInsecure()
);

// Crear un todo
client.createTodo(
  { title: 'Aprender gRPC', description: 'Completar el taller' },
  (error: any, response: any) => {
    if (error) {
      console.error('Error:', error);
      return;
    }
    console.log('Todo creado:', response);

    // Listar todos
    const listCall = client.listTodos({ show_completed: true });
    listCall.on('data', (todo: any) => {
      console.log('- Todo:', todo.title, `(${todo.completed ? 'Completado' : 'Pendiente'})`);
    });
    listCall.on('end', () => {
      console.log('Lista completa');
    });
  }
);
```

5. Agrega el script en `package.json`:

```json
"scripts": {
  "client:todo": "ts-node client/todoClient.ts"
}
```

6. Prueba el servicio:

```bash
# Terminal 1
npm run server

# Terminal 2
npm run client:todo
```

---

### Ejercicio 5: Implementar Autenticación Simple

**Objetivo:** Agregar metadata para autenticación básica.

**Tareas:**

1. Modifica el servidor para verificar un token en `server/index.ts`:

```typescript
// Interceptor de autenticación
function authInterceptor(
  call: any,
  metadata: grpc.Metadata,
  next: (error?: grpc.StatusObject) => void
) {
  const token = metadata.get('authorization')[0];

  if (!token || token !== 'Bearer mi-token-secreto') {
    const error: grpc.StatusObject = {
      code: grpc.status.UNAUTHENTICATED,
      details: 'Token inválido o ausente',
    };
    next(error);
    return;
  }

  next();
}

// Aplicar interceptor al servidor
// (nota: esto es un ejemplo simplificado, en producción usa librerías especializadas)
```

2. Actualiza el cliente para enviar el token:

```typescript
const metadata = new grpc.Metadata();
metadata.add('authorization', 'Bearer mi-token-secreto');

client.sayHello(
  { name: 'Juan', language: 'es' },
  metadata,
  (error: any, response: any) => {
    // ...
  }
);
```

---

## Ejercicios Nivel Avanzado

### Ejercicio 6: Implementar un Chat en Tiempo Real

**Objetivo:** Crear un sistema de chat usando bidirectional streaming.

**Pasos:**

1. Crea `proto/chat.proto`:

```protobuf
syntax = "proto3";

package chat;

service ChatService {
  rpc JoinChat (stream ChatMessage) returns (stream ChatMessage) {}
}

message ChatMessage {
  string user_id = 1;
  string username = 2;
  string message = 3;
  int64 timestamp = 4;
}
```

2. Implementa el servidor en `server/services/chatService.ts`:

```typescript
const clients: Set<any> = new Set();

export const chatService = {
  joinChat: (call: any) => {
    console.log('👤 Nuevo usuario en el chat');
    clients.add(call);

    call.on('data', (message: any) => {
      console.log(`💬 ${message.username}: ${message.message}`);

      // Broadcast a todos los clientes
      clients.forEach((client) => {
        if (client !== call) {  // No enviar al mismo cliente
          client.write({
            user_id: message.user_id,
            username: message.username,
            message: message.message,
            timestamp: Date.now(),
          });
        }
      });
    });

    call.on('end', () => {
      console.log('👋 Usuario salió del chat');
      clients.delete(call);
      call.end();
    });

    call.on('error', (error: Error) => {
      console.error('❌ Error en chat:', error);
      clients.delete(call);
    });
  },
};
```

3. Crea un cliente de chat interactivo.

---

### Ejercicio 7: Transferencia de Archivos

**Objetivo:** Implementar upload/download de archivos usando streaming.

**Tareas:**

1. Crea `proto/file.proto` con métodos `Upload` y `Download`
2. Implementa streaming de chunks de archivo
3. Maneja el progreso de transferencia
4. Implementa verificación de integridad (checksum)

---

### Ejercicio 8: Agregar Timeout y Retry

**Objetivo:** Implementar timeouts y reintentos en el cliente.

**Ejemplo:**

```typescript
const deadline = new Date();
deadline.setSeconds(deadline.getSeconds() + 5); // 5 segundos timeout

client.sayHello(
  { name: 'Juan' },
  { deadline: deadline.getTime() },
  (error: any, response: any) => {
    if (error && error.code === grpc.status.DEADLINE_EXCEEDED) {
      console.log('Timeout! Reintentando...');
      // Implementar lógica de retry
    }
  }
);
```

---

## Ejercicios Desafío

### Desafío 1: Sistema de Microservicios

Crea un sistema con 3 servicios:
- **UserService**: Gestión de usuarios
- **ProductService**: Catálogo de productos
- **OrderService**: Procesa órdenes (llama a User y Product)

Implementa:
- Comunicación entre servicios
- Manejo de errores distribuidos
- Health checks

---

### Desafío 2: Sistema de Notificaciones en Tiempo Real

Implementa:
- Server streaming para notificaciones push
- Diferentes tipos de notificaciones (email, SMS, push)
- Cola de prioridad
- Confirmación de entrega

---

### Desafío 3: Sistema de Logs Distribuidos

Implementa:
- Client streaming para enviar logs
- Agregación de logs de múltiples servicios
- Filtrado y búsqueda en tiempo real
- Persistencia en archivo/base de datos

---

## Verificación de Aprendizaje

### Checklist de Conceptos

Marca cada concepto cuando lo hayas entendido y aplicado:

- [ ] Definir mensajes en Protocol Buffers
- [ ] Definir servicios con diferentes tipos de RPC
- [ ] Implementar Unary RPC
- [ ] Implementar Server Streaming RPC
- [ ] Implementar Client Streaming RPC
- [ ] Implementar Bidirectional Streaming RPC
- [ ] Manejar errores con códigos gRPC
- [ ] Usar metadata para información adicional
- [ ] Implementar timeouts
- [ ] Crear servicios CRUD completos
- [ ] Entender el ciclo de vida de streams
- [ ] Implementar broadcast a múltiples clientes

---

## Recursos de Ayuda

### Comandos Útiles

```bash
# Ver procesos en el puerto 50051
lsof -i :50051

# Matar proceso en puerto específico
kill -9 $(lsof -t -i:50051)

# Ver logs del servidor en tiempo real
npm run dev:server | grep "RPC"
```

### Debugging

1. Agrega logs en métodos del servidor
2. Usa el inspector de Node.js:
   ```bash
   node --inspect server/index.ts
   ```
3. Verifica los mensajes .proto con:
   ```bash
   cat proto/greeter.proto
   ```

---

## Soluciones

Las soluciones a los ejercicios están en la carpeta `soluciones/` (crear si es necesario).

Para verificar tu solución:

1. Compara tu código con la solución
2. Ejecuta los tests (si existen)
3. Verifica que el comportamiento es el esperado

---

## Próximos Pasos

Una vez completado este taller:

1. Explora el proyecto `grpc-voice` para ver un caso de uso real
2. Lee la guía de deployment para aprender a desplegar servicios gRPC
3. Investiga sobre gRPC-Web para integración con frontend
4. Aprende sobre observabilidad (métricas, traces, logs)
5. Estudia patrones de diseño de microservicios

---

## Feedback

Si encuentras errores o tienes sugerencias para mejorar este taller, por favor crea un issue o pull request en el repositorio.

¡Feliz aprendizaje de gRPC!
