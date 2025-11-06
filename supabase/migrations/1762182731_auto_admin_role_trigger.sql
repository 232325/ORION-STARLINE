-- Migration: auto_admin_role_trigger
-- Created at: 1762182731

-- Create function to automatically create profile with admin role for specific email
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  -- Check if the email is jaloliddinsaidaliyev023@gmail.com
  IF NEW.email = 'jaloliddinsaidaliyev023@gmail.com' THEN
    -- Create profile with admin role
    INSERT INTO public.profiles (id, user_id, email, full_name, role, balance)
    VALUES (
      NEW.id,
      NEW.id,
      NEW.email,
      'Admin User',
      'admin',
      10000
    )
    ON CONFLICT (id) DO UPDATE 
    SET role = 'admin', email = NEW.email;
  ELSE
    -- Create profile with regular user role
    INSERT INTO public.profiles (id, user_id, email, full_name, role, balance)
    VALUES (
      NEW.id,
      NEW.id,
      NEW.email,
      COALESCE(NEW.raw_user_meta_data->>'full_name', ''),
      'user',
      0
    )
    ON CONFLICT (id) DO NOTHING;
  END IF;
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Drop existing trigger if exists
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;

-- Create trigger that fires after user is created
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW
  EXECUTE FUNCTION public.handle_new_user();;