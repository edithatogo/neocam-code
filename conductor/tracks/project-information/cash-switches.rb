# Calculate the upper envelope of six linear cash schedules relative to telephone.
require 'csv'
data = CSV.read('verification/mixed-policy-fiscal/chhhs-cash.csv', headers: true)
[3, 5].each do |horizon|
  totals = data.select { |r| r['year'].to_i <= horizon }.group_by { |r| r['policy'] }.transform_values do |rows|
    fixed = rows.sum { |r| r['fixed_contract_no_care_cash'].to_f }
    variable = rows.sum { |r| r['variable_retrieval_no_care_cash'].to_f }
    [fixed, variable - fixed]
  end
  breaks = totals.values.combination(2).map do |(a,b),(c,d)|
    next if (b-d).abs < 1e-8
    x = (c-a)/(b-d)
    x if x.between?(0,1)
  end
  previous = nil
  ([0.0,1.0]+breaks.compact).uniq.sort.each_cons(2) do |lo,hi|
    winner = totals.max_by { |_,(a,b)| a+b*(lo+hi)/2 }.first
    puts [horizon,lo,winner].join(',') unless previous == winner
    previous = winner
  end
end
