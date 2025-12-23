import * as grpc from '@grpc/grpc-js';
import * as protoLoader from '@grpc/proto-loader';
import path from 'path';
import { greeterService } from './services/greeterService';
import { calculatorService } from './services/calculatorService';

// Configuración de carga de proto files
const PROTO_PATH_GREETER = path.join(__dirname, '../proto/greeter.proto');
const PROTO_PATH_CALCULATOR = path.join(__dirname, '../proto/calculator.proto');

const packageDefinitionOptions = {
  keepCase: true,
  longs: String,
  enums: String,
  defaults: true,
  oneofs: true,
};

// Cargar las definiciones de proto
const greeterPackageDef = protoLoader.loadSync(PROTO_PATH_GREETER, packageDefinitionOptions);
const calculatorPackageDef = protoLoader.loadSync(PROTO_PATH_CALCULATOR, packageDefinitionOptions);

const greeterProto = grpc.loadPackageDefinition(greeterPackageDef) as any;
const calculatorProto = grpc.loadPackageDefinition(calculatorPackageDef) as any;

// Crear servidor gRPC
const server = new grpc.Server();

// Agregar servicios al servidor
server.addService(greeterProto.greeter.Greeter.service, greeterService);
server.addService(calculatorProto.calculator.Calculator.service, calculatorService);

// Configurar puerto y arrancar servidor
const PORT = process.env.PORT || '50051';
const HOST = '0.0.0.0';

server.bindAsync(
  `${HOST}:${PORT}`,
  grpc.ServerCredentials.createInsecure(),
  (error, port) => {
    if (error) {
      console.error('Error al iniciar el servidor:', error);
      return;
    }
    console.log(`\n🚀 Servidor gRPC ejecutándose en ${HOST}:${port}`);
    console.log('\n📋 Servicios disponibles:');
    console.log('  - Greeter Service (greeter.proto)');
    console.log('  - Calculator Service (calculator.proto)');
    console.log('\n✅ El servidor está listo para recibir peticiones\n');
  }
);
