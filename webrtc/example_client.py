"""
Cliente de ejemplo para demostrar el uso de la API con concurrencia
Ejecuta múltiples operaciones en paralelo usando asyncio
"""

import asyncio
import aiohttp
import json
from datetime import datetime


BASE_URL = "http://localhost:8000"


async def create_item(session: aiohttp.ClientSession, title: str, status: str = "active"):
    """Crea un item de forma asíncrona"""
    async with session.post(
        f"{BASE_URL}/api/items/",
        json={"title": title, "description": f"Creado por cliente Python", "status": status}
    ) as response:
        if response.status == 201:
            data = await response.json()
            print(f"✓ Item creado: {data['title']} (ID: {data['id']})")
            return data
        else:
            print(f"✗ Error al crear item: {response.status}")
            return None


async def get_items(session: aiohttp.ClientSession):
    """Obtiene todos los items"""
    async with session.get(f"{BASE_URL}/api/items/") as response:
        if response.status == 200:
            data = await response.json()
            print(f"✓ Items obtenidos: {len(data)}")
            return data
        return []


async def update_item(session: aiohttp.ClientSession, item_id: int, new_status: str):
    """Actualiza un item"""
    async with session.put(
        f"{BASE_URL}/api/items/{item_id}",
        json={"status": new_status}
    ) as response:
        if response.status == 200:
            data = await response.json()
            print(f"✓ Item {item_id} actualizado a {new_status}")
            return data
        return None


async def delete_item(session: aiohttp.ClientSession, item_id: int):
    """Elimina un item"""
    async with session.delete(f"{BASE_URL}/api/items/{item_id}") as response:
        if response.status == 204:
            print(f"✓ Item {item_id} eliminado")
            return True
        return False


async def demo_concurrent_creation():
    """
    Demuestra creación concurrente de múltiples items
    """
    print("\n" + "="*60)
    print("DEMO: Creación Concurrente de Items")
    print("="*60)

    async with aiohttp.ClientSession() as session:
        # Crear 10 items en paralelo
        tasks = []
        for i in range(1, 11):
            task = create_item(
                session,
                f"Item Concurrente {i}",
                ["active", "pending", "inactive"][i % 3]
            )
            tasks.append(task)

        start = datetime.now()
        results = await asyncio.gather(*tasks)
        end = datetime.now()

        successful = sum(1 for r in results if r is not None)
        print(f"\n✓ Creados {successful} items en paralelo")
        print(f"⏱  Tiempo total: {(end - start).total_seconds():.2f}s")
        return results


async def demo_bulk_operations():
    """
    Demuestra operaciones bulk usando el endpoint específico
    """
    print("\n" + "="*60)
    print("DEMO: Operaciones Bulk")
    print("="*60)

    async with aiohttp.ClientSession() as session:
        # Crear múltiples items usando el endpoint bulk
        bulk_data = [
            {"title": f"Bulk Item {i}", "status": "active", "description": "Creado en bulk"}
            for i in range(1, 6)
        ]

        start = datetime.now()
        async with session.post(f"{BASE_URL}/api/items/bulk", json=bulk_data) as response:
            if response.status == 201:
                data = await response.json()
                end = datetime.now()
                print(f"✓ {len(data)} items creados via bulk endpoint")
                print(f"⏱  Tiempo: {(end - start).total_seconds():.2f}s")

                # Obtener IDs de los items creados
                item_ids = [item['id'] for item in data]

                # Actualizar status en bulk
                await asyncio.sleep(1)
                start = datetime.now()
                async with session.patch(
                    f"{BASE_URL}/api/items/bulk/status?new_status=inactive",
                    json=item_ids
                ) as update_response:
                    if update_response.status == 200:
                        result = await update_response.json()
                        end = datetime.now()
                        print(f"✓ {result['updated_count']} items actualizados en bulk")
                        print(f"⏱  Tiempo: {(end - start).total_seconds():.2f}s")


async def demo_crud_operations():
    """
    Demuestra operaciones CRUD básicas
    """
    print("\n" + "="*60)
    print("DEMO: Operaciones CRUD Básicas")
    print("="*60)

    async with aiohttp.ClientSession() as session:
        # CREATE
        print("\n1. CREATE")
        item = await create_item(session, "Item de Prueba CRUD", "active")

        if not item:
            return

        item_id = item['id']

        # READ
        print("\n2. READ")
        await asyncio.sleep(0.5)
        async with session.get(f"{BASE_URL}/api/items/{item_id}") as response:
            if response.status == 200:
                data = await response.json()
                print(f"✓ Item leído: {data['title']}")

        # UPDATE
        print("\n3. UPDATE")
        await asyncio.sleep(0.5)
        await update_item(session, item_id, "pending")

        # READ (verificar update)
        async with session.get(f"{BASE_URL}/api/items/{item_id}") as response:
            if response.status == 200:
                data = await response.json()
                print(f"✓ Status verificado: {data['status']}")

        # DELETE
        print("\n4. DELETE")
        await asyncio.sleep(0.5)
        await delete_item(session, item_id)

        # Verificar eliminación
        async with session.get(f"{BASE_URL}/api/items/{item_id}") as response:
            if response.status == 404:
                print("✓ Eliminación verificada (404)")


async def demo_parallel_operations():
    """
    Demuestra múltiples operaciones diferentes ejecutándose en paralelo
    """
    print("\n" + "="*60)
    print("DEMO: Operaciones Paralelas Mixtas")
    print("="*60)

    async with aiohttp.ClientSession() as session:
        # Ejecutar múltiples operaciones diferentes al mismo tiempo
        start = datetime.now()

        results = await asyncio.gather(
            create_item(session, "Paralelo 1", "active"),
            create_item(session, "Paralelo 2", "inactive"),
            create_item(session, "Paralelo 3", "pending"),
            get_items(session),
            return_exceptions=True
        )

        end = datetime.now()

        successful = sum(1 for r in results if r is not None and not isinstance(r, Exception))
        print(f"\n✓ {successful} operaciones completadas en paralelo")
        print(f"⏱  Tiempo total: {(end - start).total_seconds():.2f}s")


async def main():
    """
    Función principal que ejecuta todas las demos
    """
    print("\n" + "="*60)
    print("CLIENTE DE EJEMPLO - API WebRTC CRUD")
    print("Demostrando Concurrencia y Paralelismo")
    print("="*60)

    try:
        # Verificar que el servidor esté corriendo
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/health") as response:
                if response.status == 200:
                    print("\n✓ Servidor conectado correctamente\n")
                else:
                    print("\n✗ Error al conectar con el servidor")
                    return

        # Ejecutar demos
        await demo_crud_operations()
        await asyncio.sleep(1)

        await demo_concurrent_creation()
        await asyncio.sleep(1)

        await demo_bulk_operations()
        await asyncio.sleep(1)

        await demo_parallel_operations()

        print("\n" + "="*60)
        print("DEMOS COMPLETADAS")
        print("="*60 + "\n")

    except aiohttp.ClientError as e:
        print(f"\n✗ Error de conexión: {e}")
        print("¿Está el servidor corriendo en http://localhost:8000?")
    except Exception as e:
        print(f"\n✗ Error inesperado: {e}")


if __name__ == "__main__":
    asyncio.run(main())
