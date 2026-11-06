-- ========================================================
-- BOXINERA IMPORTADORA - SUPABASE SCHEMA & SECURITY POLICIES
-- ========================================================

-- 1. CREAR TABLA DE PRODUCTOS
create table if not exists public.products (
  id bigint primary key,
  code text,
  name text not null,
  brand text not null,
  category text not null,
  line text,
  details text,
  color text,
  ml text,
  gender text,
  price numeric not null,
  old_price numeric,
  badge text,
  image text,
  in_stock boolean default true,
  wholesale jsonb,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- 2. HABILITAR SEGURIDAD POR FILAS (ROW LEVEL SECURITY - RLS)
alter table public.products enable row level security;

-- 3. POLÍTICAS DE SEGURIDAD
-- Lectura pública: Cualquier cliente que visite la tienda web puede ver los productos
create policy "Public products are viewable by everyone"
  on public.products for select
  using (true);

-- Escritura protegida: Solo el dueño autenticado puede crear productos
create policy "Only authenticated owner can insert products"
  on public.products for insert
  with check (auth.role() = 'authenticated');

-- Modificación protegida: Solo el dueño autenticado puede cambiar precios o editar productos
create policy "Only authenticated owner can update products"
  on public.products for update
  using (auth.role() = 'authenticated');

-- Eliminación protegida: Solo el dueño autenticado puede borrar productos
create policy "Only authenticated owner can delete products"
  on public.products for delete
  using (auth.role() = 'authenticated');

-- 4. HABILITAR SINCRONIZACIÓN EN TIEMPO REAL (REALTIME)
alter publication supabase_realtime add table public.products;

-- 5. CREAR STORAGE BUCKET PARA FOTOS DE PRODUCTOS (OPCIONAL)
insert into storage.buckets (id, name, public) 
values ('product-images', 'product-images', true)
on conflict (id) do nothing;

create policy "Public images access"
  on storage.objects for select
  using (bucket_id = 'product-images');

create policy "Owner image upload"
  on storage.objects for insert
  with check (bucket_id = 'product-images' and auth.role() = 'authenticated');
