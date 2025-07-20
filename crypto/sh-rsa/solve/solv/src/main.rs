use hashbrown::HashMap;
use indicatif::{ProgressBar, ProgressStyle};
use rayon::prelude::*;
use rug::Integer;
use std::collections::VecDeque;
use std::io::{self, BufRead};

fn msb_clamped(number: u128, num_bits: u32) -> u128 {
    if number == 0 {
        return 0;
    }
    let bit_length = 128 - number.leading_zeros();
    if bit_length <= num_bits {
        return number;
    }
    number >> (bit_length - num_bits)
}

fn bitmap_product(elements: &[u128], bitmap: u32) -> Integer {
    let mut result = Integer::from(1);
    let mut temp_bitmap = bitmap;
    let mut idx = 0;

    while temp_bitmap != 0 {
        if temp_bitmap & 1 != 0 {
            result = result * Integer::from(elements[idx]);
        }
        temp_bitmap >>= 1;
        idx += 1;
    }

    result
}

fn combined_bitmap_product(lists: &[&[u128]], bitmap: u128) -> Integer {
    let mut result = Integer::from(1);
    for (i, list) in lists.iter().enumerate() {
        let list_bitmap = ((bitmap >> (i * 32)) & 0xFFFFFFFF) as u32;
        result *= bitmap_product(list, list_bitmap);
    }
    result
}

fn tree_based_subset_products(
    elements: &[u128],
    max_bits: u32,
    key_bits: u32,
) -> HashMap<u128, Vec<(u32, u128)>> {
    let n = elements.len();

    let expected_entries = 1usize << (n - 1);
    let mut result: HashMap<u128, Vec<(u32, u128)>> = HashMap::with_capacity(expected_entries);

    let clamped_elements: Vec<u128> = elements
        .par_iter()
        .map(|&elem| msb_clamped(elem, max_bits))
        .collect();

    let mut queue: VecDeque<(usize, u128, u32)> = VecDeque::new();
    queue.push_back((0, 1, 0));

    let total = 1u64 << n;
    let pb = ProgressBar::new(total);
    pb.set_style(
        ProgressStyle::default_bar()
            .template(
                "{spinner:.green} [{elapsed_precise}] [{bar:40.cyan/blue}] {pos}/{len} ({eta})",
            )
            .unwrap(),
    );

    while !queue.is_empty() {
        if let Some((index, current_product, current_bitmap)) = queue.pop_front() {
            if index == n {
                pb.inc(1);
                if current_bitmap != 0 {
                    let product_key = msb_clamped(current_product, key_bits);
                    result
                        .entry(product_key)
                        .or_insert_with(Vec::new)
                        .push((current_bitmap, current_product));
                }
                continue;
            }
            queue.push_back((index + 1, current_product, current_bitmap));
            let new_bitmap = current_bitmap | (1u32 << index);
            let new_product = msb_clamped(current_product * clamped_elements[index], max_bits);
            queue.push_back((index + 1, new_product, new_bitmap));
        }
    }

    pb.finish();
    result
}

fn solve(t: u128, l1: Vec<u128>, l2: Vec<u128>, l3: Vec<u128>, l4: Vec<u128>) {
    let t_bits = 128 - t.leading_zeros();
    eprintln!("t = {:x}, t_bits = {}", t, t_bits);

    let t0 = 0b101010101010101010101u128;
    let t_bits_div3: u32 = t_bits.div_ceil(3);

    let t0_lb = t0 << t_bits_div3;

    let t_msb = msb_clamped(t, t_bits_div3);
    let t1_lb = msb_clamped((t_msb << t_bits_div3) / t0, t_bits_div3) << t_bits_div3;

    let start = std::time::Instant::now();

    eprintln!("Building U1 lookup table...");
    let u1 = tree_based_subset_products(&l1, 64, t_bits_div3);
    eprintln!("U1 contains {} entries", u1.len());

    eprintln!("Building U2 lookup table...");
    let u2 = tree_based_subset_products(&l2, 64, t_bits_div3);
    eprintln!("U2 contains {} entries", u2.len());

    eprintln!("Building S12...");
    let pb = ProgressBar::new(u2.len() as u64);
    pb.set_style(
        ProgressStyle::default_bar()
            .template(
                "{spinner:.green} [{elapsed_precise}] [{bar:40.cyan/blue}] {pos}/{len} ({eta})",
            )
            .unwrap(),
    );

    let u2_keys: Vec<u128> = u2.keys().cloned().collect();
    let s12: Vec<(u64, u128)> = (0..u2_keys.len())
        .into_par_iter()
        .flat_map(|idx| {
            pb.inc(1);
            let v2 = &u2_keys[idx];
            let entries_v2 = &u2[v2];
            let mut local_results = Vec::new();
            let lb = t0_lb / v2;
            for v1_offset in 0..=2 {
                let v1 = lb + v1_offset;
                if let Some(entries_v1) = u1.get(&v1) {
                    for &(bitmap_c1, t1) in entries_v1 {
                        for &(bitmap_c2, t2) in entries_v2 {
                            let combined_bitmap = bitmap_c1 as u64 | ((bitmap_c2 as u64) << 32);
                            let product_value = msb_clamped(t1 * t2, t_bits);
                            local_results.push((combined_bitmap, product_value));
                        }
                    }
                }
            }
            local_results
        })
        .collect();

    pb.finish();
    eprintln!("S12 contains {} entries", s12.len());

    eprintln!("Building U3 lookup table...");
    let u3 = tree_based_subset_products(&l3, 64, t_bits_div3);
    eprintln!("U3 contains {} entries", u3.len());

    eprintln!("Building U4 lookup table...");
    let u4 = tree_based_subset_products(&l4, 64, t_bits_div3);
    eprintln!("U4 contains {} entries", u4.len());

    eprintln!("Building S34...");
    let pb = ProgressBar::new(u4.len() as u64);
    pb.set_style(
        ProgressStyle::default_bar()
            .template(
                "{spinner:.green} [{elapsed_precise}] [{bar:40.cyan/blue}] {pos}/{len} ({eta})",
            )
            .unwrap(),
    );

    let mut s34 = HashMap::with_capacity(if u1.len() == 23 {
        14_000_000
    } else {
        8_000_000
    });

    let chunk_size = 2048;
    let u4_keys: Vec<u128> = u4.keys().cloned().collect();
    let num_chunks = (u4_keys.len() + chunk_size - 1) / chunk_size;

    for chunk_idx in 0..num_chunks {
        let start = chunk_idx * chunk_size;
        let end = (start + chunk_size).min(u4_keys.len());

        let chunk_maps: Vec<HashMap<u128, (u64, u128)>> = (start..end)
            .into_par_iter()
            .map(|idx| {
                let v4 = &u4_keys[idx];
                let entries_v4 = &u4[v4];
                pb.inc(1);

                let mut local_map = HashMap::new();

                let lb = t1_lb / v4;
                for v3_offset in 0..=2 {
                    let v3 = lb + v3_offset;

                    if let Some(entries_v3) = u3.get(&v3) {
                        for &(bitmap_c3, t3) in entries_v3 {
                            for &(bitmap_c4, t4) in entries_v4 {
                                let combined_bitmap = bitmap_c3 as u64 | ((bitmap_c4 as u64) << 32);

                                let product_value = msb_clamped(t3 * t4, t_bits);
                                let key = msb_clamped(t3 * t4, 2 * t_bits_div3);

                                local_map.insert(key, (combined_bitmap, product_value));
                            }
                        }
                    }
                }

                local_map
            })
            .collect();

        for map in chunk_maps {
            s34.extend(map);
        }
    }

    pb.finish();
    eprintln!("S34 contains {} entries", s34.len());

    eprintln!("Performing final search...");
    let pb = ProgressBar::new(s12.len() as u64);
    pb.set_style(
        ProgressStyle::default_bar()
            .template(
                "{spinner:.green} [{elapsed_precise}] [{bar:40.cyan/blue}] {pos}/{len} ({eta})",
            )
            .unwrap(),
    );

    let t_lb = msb_clamped(t, 2 * t_bits_div3) << (2 * t_bits_div3);

    s12.into_par_iter().find_any(|&(bitmap_c12, t12)| {
        pb.inc(1);

        let t12c = msb_clamped(t12, 2 * t_bits_div3);
        let lb = t_lb / t12c;

        for v34_offset in 0..=2 {
            let v34 = lb + v34_offset;

            if let Some(&(bitmap_c34, t34)) = s34.get(&v34) {
                if msb_clamped(t12 * t34, t_bits - 8) == msb_clamped(t, t_bits - 8) {
                    let bitmap_l1 = (bitmap_c12 & 0xFFFFFFFF) as u32;
                    let bitmap_l2 = ((bitmap_c12 >> 32) & 0xFFFFFFFF) as u32;
                    let bitmap_l3 = (bitmap_c34 & 0xFFFFFFFF) as u32;
                    let bitmap_l4 = ((bitmap_c34 >> 32) & 0xFFFFFFFF) as u32;

                    let combined_bitmap = (bitmap_l1 as u128)
                        | ((bitmap_l2 as u128) << 32)
                        | ((bitmap_l3 as u128) << 64)
                        | ((bitmap_l4 as u128) << 96);

                    let lists = [&l1[..], &l2[..], &l3[..], &l4[..]];
                    let full_product = combined_bitmap_product(&lists, combined_bitmap);
                    if full_product.significant_bits() % 8 != 0 {
                        continue;
                    }

                    if full_product
                        .to_string_radix(16)
                        .starts_with(&Integer::from(t).to_string_radix(16))
                    {
                        eprintln!(
                            "Found solution: Product = {}",
                            full_product.to_string_radix(16),
                        );

                        println!("{}", combined_bitmap);

                        return true;
                    }
                }
            }
        }

        false
    });

    pb.finish();

    eprintln!("Total time: {:?}", start.elapsed());
}

fn main() {
    let stdin = io::stdin();
    let mut lines = stdin.lock().lines();

    let t_str = lines
        .next()
        .expect("Expected input for t")
        .expect("Failed to read t");
    let t = u128::from_str_radix(&t_str, 16).expect("Failed to parse t as hex");

    let list_size = 32;
    let mut l1 = Vec::with_capacity(list_size);
    let mut l2 = Vec::with_capacity(list_size);
    let mut l3 = Vec::with_capacity(list_size);
    let mut l4 = Vec::with_capacity(list_size);

    for list_idx in 0..4 {
        let line = lines
            .next()
            .expect(&format!("Expected input for list {}", list_idx + 1))
            .expect(&format!("Failed to read list {}", list_idx + 1));

        let numbers: Vec<u128> = line
            .split_whitespace()
            .map(|s| {
                s.parse::<u128>()
                    .expect(&format!("Failed to parse number in list {}", list_idx + 1))
            })
            .collect();

        match list_idx {
            0 => l1 = numbers,
            1 => l2 = numbers,
            2 => l3 = numbers,
            3 => l4 = numbers,
            _ => unreachable!(),
        }
    }

    solve(t, l1, l2, l3, l4);
}

#[cfg(test)]
mod tests {
    use super::*;
    use rand::{thread_rng, RngCore};

    #[test]
    fn test_with_hardcoded_values() {
        let t = u128::from_str_radix("8444444444444444", 16).unwrap();

        let n = 4 * 23;
        let mut mi = vec![0u128; n];
        let mut rng = thread_rng();
        for val in mi.iter_mut() {
            *val = rng.next_u64() as u128;
        }

        let list_size = n / 4;
        let l1: Vec<u128> = mi[0..list_size].to_vec();
        let l2: Vec<u128> = mi[list_size..2 * list_size].to_vec();
        let l3: Vec<u128> = mi[2 * list_size..3 * list_size].to_vec();
        let l4: Vec<u128> = mi[3 * list_size..4 * list_size].to_vec();

        solve(t, l1, l2, l3, l4);
    }
}
