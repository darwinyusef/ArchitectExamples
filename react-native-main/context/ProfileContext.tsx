import AsyncStorage from "@react-native-async-storage/async-storage";
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

const STORE_KEY = "profile:v1";

export type Profile = {
  name: string;
  role: string;
  avatarUri?: string | null; // local/remote
};

type Ctx = {
  loading: boolean;
  profile: Profile;
  updateProfile: (patch: Partial<Profile>) => Promise<void>;
  setAvatar: (uri: string | null) => Promise<void>;
};

const defaultProfile: Profile = {
  name: "Tu nombre",
  role: "Profesión",
  avatarUri: null,
};

const ProfileContext = createContext<Ctx>({
  loading: true,
  profile: defaultProfile,
  updateProfile: async () => {},
  setAvatar: async () => {},
});

export const useProfile = () => useContext(ProfileContext);

export function ProfileProvider({ children }: { children: React.ReactNode }) {
  const [loading, setLoading] = useState(true);
  const [profile, setProfile] = useState<Profile>(defaultProfile);

  useEffect(() => {
    (async () => {
      try {
        const raw = await AsyncStorage.getItem(STORE_KEY);
        if (raw) setProfile(JSON.parse(raw));
      } catch (error) {
        console.warn("Profile load error", error);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const persist = useCallback(async (p: Profile) => {
    setProfile(p);
    try {
      await AsyncStorage.setItem(STORE_KEY, JSON.stringify(p));
    } catch (e) {
      console.warn("Profile save error", e);
    }
  }, []);

  const updateProfile = useCallback(
    async (patch: Partial<Profile>) => {
      await persist({ ...profile, ...patch });
    },
    [profile, persist]
  );

  const setAvatar = useCallback(
    async (uri: string | null) => {
      await persist({ ...profile, avatarUri: uri });
    },
    [profile, persist]
  );

  const value = useMemo(
    () => ({ loading, profile, updateProfile, setAvatar }),
    [loading, profile, updateProfile, setAvatar]
  );

  return (
    <ProfileContext.Provider value={value}>{children}</ProfileContext.Provider>
  );
}
